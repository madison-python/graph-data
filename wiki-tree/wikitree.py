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
    table.insert(0, 'title', title)
    table.rename(columns=lambda x: x.lstrip('_'), inplace=True)
    logger.info('Retrieved {} revisions for article "{}"'.format(
                len(table), title))
    return table


def get_page(title):
    site = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(site, title)
    return page


def graph_revisions(revisions):
    graph = Graph(password=environ['NEO4J_PASSWORD'])

    # Create nodes for every article
    articles = {title: Node('Article', title=title)
                for title in revisions.title.unique()}

    # Create nodes for every version of the article
    texts = {sha1: Node('Wikitext', sha1=sha1)
             for sha1 in revisions.sha1.unique()}

    # Create a dict of revid -> sha1
    sha1s = (revisions[['revid', 'sha1']]
                      .set_index('revid')
                      .squeeze()  # single column DataFrame -> Series
                      .to_dict())

    # Create relationships for every edit to the article
    first_edit = True
    edits, versions = [], []
    for rev in revisions.itertuples():
        if rev.parent_id == 0:
            # skip revisions without parents
            continue

        parent_sha1 = sha1s.get(rev.parent_id)
        if parent_sha1 is None:
            logger.info('Parent revision #{} not found'.format(rev.parent_id))
            parent_sha1 = hashlib.sha1(str(rev.parent_id).encode()).hexdigest()
            sha1s[rev.parent_id] = parent_sha1
            texts[parent_sha1] = Node('Wikitext', sha1=parent_sha1)

        child = texts[rev.sha1]
        parent = texts[parent_sha1]

        # A hacky way to ensure it's easy to find the root node
        if first_edit:
            parent['type'] = 'root'
            first_edit = False

        edit = Relationship(parent, 'EDIT', child)
        edits.append(edit)

        article = articles[rev.title]
        version = Relationship(article, 'VERSION', child)
        versions.append(version)


    # Smells!
    for text in texts.values():
        graph.merge(text, label='Wikitext')
    for article in texts.values():
        graph.merge(article, label='Article')
    for edit in edits:
        graph.merge(edit, label='Wikitext')
    for version in versions:
        graph.merge(version, label='Article')


class ParentRevisionNotFound(Exception):
    """The parent revision was not found but it should have been."""


class WikiTree:
    def graph(self, title, limit=None, verbose=False):
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
        graph_revisions(revisions)

    def count(self, title):
        page = get_page(title)
        print('The Wikipedia article on "{}" has {} revisions'.format(
              title, page.revision_count()))

if __name__ == '__main__':
    fire.Fire(WikiTree())
