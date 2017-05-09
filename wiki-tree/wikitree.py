#!/usr/bin/env python
from os import environ
from sys import stdout

import pywikibot
import pandas
import fire
from py2neo import Graph, Node, Relationship, Subgraph


def get_revisions(title):
    page = get_wiki_page(title)
    revisions = page.revisions(content=False)
    records = [revision.__dict__ for revision in revisions]
    table = pandas.DataFrame.from_records(records)
    table.insert(0, 'title', title)
    table.rename(columns={'_sha1': 'sha1', '_parent_id': 'parent_id'},
                 inplace=True)
    return table


def get_wiki_page(title):
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
    edits, versions = [], []
    for rev in revisions.itertuples():
        if rev.parent_id == 0:
            # skip revisions without parents
            continue

        parent_sha1 = sha1s.get(rev.parent_id)
        if parent_sha1 is None:
            raise ParentRevisionNotFound('revid#{}'.format(rev.revid))

        child = texts[rev.sha1]
        parent = texts[parent_sha1]
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
    """A simple CLI for loading article revision histories into Neo4j."""
    def download(self, title, output=None):
        """Download the revisions for an article."""
        revisions = get_revisions(title)
        revisions.to_csv(output or stdout, index=False)

    def graph(self, title, open_after=False):
        """Load the revisions for an article into a graph database."""
        revisions = get_revisions(title)
        graph_revisions(revisions)


if __name__ == '__main__':
    fire.Fire(WikiTree())
