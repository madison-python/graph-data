#!/usr/bin/env python
import logging
import hashlib
from os import environ
from sys import stdout

import pywikibot
import pandas
import fire
from py2neo import Graph, Node, Relationship, Subgraph


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def get_revisions(title, limit=None):
    """Retrieve all versions of a Wikipedia article."""
    page = get_page(title)
    limit = limit or page.revision_count()
    revisions = page.revisions(content=False)
    records = [next(revisions).__dict__ for _ in range(limit)]
    table = pandas.DataFrame.from_records(records)
    table.sort_values('timestamp', inplace=True)
    table.reset_index(drop=True)
    table.insert(0, 'title', title)
    table.rename(columns=lambda x: x.lstrip('_'), inplace=True)
    logger.info('Retrieved {} revisions for article "{}"'.format(
                len(table), title))
    return table


def get_page(title):
    site = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(site, title)
    return page


def graph_revisions(table, delete=False):
    graph = Graph(password=environ['NEO4J_PASSWORD'])

    if delete:
        graph.run('MATCH (n) DETACH DELETE n')

    # Create nodes for every article
    assert len(table.title.unique()) == 1
    article = Node('Article', title=table.title.iloc[0])

    # Create nodes for every revision
    revisions = {revid: Node('Revision', revid=int(revid))
                 for revid in table.revid.unique()}

    # Create nodes for every text version
    wikitexts = {sha1: Node('Wikitext', sha1=sha1)
                 for sha1 in table.sha1.unique()}

    # Create a dict of revid -> sha1
    sha1s = (table[['revid', 'sha1']]
                  .set_index('revid')
                  .squeeze()  # single column DataFrame -> Series
                  .to_dict())

    # Create relationships for every edit to the article
    first_edit = True
    relationships = []
    for rev in table.itertuples():
        if rev.parent_id == 0:
            # skip revisions without parents
            continue

        child_rev = revisions[rev.revid]
        child_text = wikitexts[rev.sha1]

        parent_rev = revisions[rev.parent_id]
        parent_sha1 = sha1s[rev.parent_id]
        parent_text = wikitexts[parent_sha1]

        if first_edit:
            parent_rev['type'] = 'root'
            first_edit = False
            relationships.extend([
                Relationship(parent_rev, 'CONTAINS', parent_text),
                Relationship(parent_rev, 'TO', article),
            ])

        relationships.extend([
            Relationship(child_text, 'VERSION', article),
            Relationship(child_rev, 'TO', article),
            Relationship(child_rev, 'CONTAINS', child_text),
            Relationship(parent_rev, 'NEXT', child_rev),
            Relationship(parent_text, 'EDIT', child_text)
        ])


    # Smells!
    graph.merge(article, label='Article')
    for revision in revisions.values():
        graph.merge(revision, label='Revision')
    for wikitext in wikitexts.values():
        graph.merge(wikitext, label='Wikitext')
    for relationship in relationships:
        graph.merge(relationship)


class ParentRevisionNotFound(Exception):
    """The parent revision was not found but it should have been."""


class WikiTree:
    def graph(self, title, delete=False, limit=None, verbose=False):
        """Graph the revision history of a Wikipedia article.

        Args:
            title (str): The name or slug of an English Wikipedia article.
            limit (int): Limit the number of revisions. If not specified,
                all revisions will be returned.
            verbose (bool): Print stuff for debugging.
        """
        if verbose:
            logger.setLevel(logging.INFO)
        revisions = get_revisions(title, limit=limit)
        graph_revisions(revisions, delete=delete)

    def count(self, title):
        page = get_page(title)
        print('The Wikipedia article on "{}" has {} revisions'.format(
              title, page.revision_count()))

if __name__ == '__main__':
    fire.Fire(WikiTree())
