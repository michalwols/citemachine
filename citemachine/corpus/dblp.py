# Assumed format (V6):
# #* --- paperTitle
# #@ --- Authors
# #year ---- Year
# #conf --- publication venue
# #citation --- citation number (both -1 and 0 means none)
# #index ---- index id of this paper
# #arnetid ---- pid in arnetminer database
# #% ---- the id of references of this paper (there are multiple lines,
#     with each indicating a reference)
# #! --- Abstract

# NOTE: Some fields might be missing!
# DATA URL: http://arnetminer.org/citation


class DBLP(object):

    def __init__(self, src, max_docs=None, only_with_refs_and_abstracts=True):
        """Be default only stores records which contain an abstract and
           a list of references"""
        self.titles = {}
        self.authors = {}
        self.years = {}
        self.conferences = {}
        self.citation_counts = {}
        self.references = {}
        self.abstracts = {}

        title = auth = year = conf = cite_count = doc_id = \
            line = refs = abstract = None

        with open(src, 'r') as document:

            # first line includes the number of citation links
            document.readline()
            line = document.readline()

            num_docs = 0
            while line:

                if line.startswith('#*'):
                    title = line[2:].rstrip()
                    line = document.readline()

                if line.startswith('#@'):
                    auth = line[2:].rstrip().split(',')
                    line = document.readline()

                if line.startswith('#year'):
                    year = line[5:].rstrip()
                    line = document.readline()

                if line.startswith('#conf'):
                    conf = line[5:].rstrip()
                    line = document.readline()

                if line.startswith('#citation'):
                    cite_count = int(line[9:].rstrip())
                    line = document.readline()

                if line.startswith('#index'):
                    doc_id = line[6:].rstrip()
                    line = document.readline()

                if line.startswith('#arnetid'):
                    line = document.readline()

                if line.startswith('#%'):
                    refs = []
                    while line.startswith('#%'):
                        refs.append(line[2:].rstrip())
                        line = document.readline()

                if line.startswith('#!'):
                    abstract = line[2:].rstrip()
                    line = document.readline()

                # parsed full record
                if line == '\n':

                    if only_with_refs_and_abstracts:
                        if refs and abstract:
                            self.titles[doc_id] = title
                            self.authors[doc_id] = auth
                            self.years[doc_id] = year
                            self.conferences[doc_id] = conf
                            self.citation_counts[doc_id] = cite_count
                            self.references[doc_id] = refs
                            self.abstracts[doc_id] = abstract
                            num_docs += 1
                    else:
                        self.titles[doc_id] = title
                        self.authors[doc_id] = auth
                        self.years[doc_id] = year
                        self.conferences[doc_id] = conf
                        self.citation_counts[doc_id] = cite_count
                        if refs:
                            self.references[doc_id] = refs
                        if abstract:
                            self.abstracts[doc_id] = abstract
                        num_docs += 1

                    if max_docs and num_docs >= max_docs:
                        break

                    title = auth = year = conf = cite_count = doc_id = \
                        line = refs = abstract = None

                line = document.readline()

    def remove_out_of_index_references(self):
        """Removes all references to documents that are not in the index

        NOTE: After removing the references, some documents might be left
              with no references
        """
        index = set(self.ids())
        is_in_index = lambda ref: ref in index

        for doc_id in index:
            self.references[doc_id] = filter(is_in_index,
                                             self.references[doc_id])

    def get_text(self, doc_id):
        """Returns all of the text for the document"""
        return self.titles[doc_id] + ' ' + self.abstracts[doc_id]

    def ids(self):
        """Returns ids of all documents in the index"""
        return self.titles.keys()

    def pop(self, doc_id, default=0):
        """Remove doc_id from index"""
        self.titles.pop(doc_id, default)
        self.authors.pop(doc_id, default)
        self.years.pop(doc_id, default)
        self.conferences.pop(doc_id, default)
        self.citation_counts.pop(doc_id, default)
        self.references.pop(doc_id, default)
        self.abstracts.pop(doc_id, default)


def parse_to_doc_dict(src, max_docs=None):
    """Parses a DBLP file

    Args:
        src: path to DBLP file
        max_docs: sets a limit on how many documents to load from file
    Returns:
        docs: dictionary mapping from document ids to document reference dicts
            docs[doc_id] -> doc, doc[field_name] -> field_value
            where field_name can be one of:
                "title", "authors", "year", "conference", "abstract",
                "citation_count", "id", "arnedid", references"
    """
    docs = {}

    with open(src, 'r') as document:

        # first line includes the number of citation links
        document.readline()
        line = document.readline()

        num_docs = 0
        doc = {}
        while line:

            if line.startswith('#*'):
                doc['title'] = line[2:].rstrip()
                line = document.readline()

            if line.startswith('#@'):
                doc['authors'] = line[2:].rstrip().split(',')
                line = document.readline()

            if line.startswith('#year'):
                doc['year'] = line[5:].rstrip()
                line = document.readline()

            if line.startswith('#conf'):
                doc['conference'] = line[5:].rstrip()
                line = document.readline()

            if line.startswith('#citation'):
                doc['citation_count'] = int(line[9:].rstrip())
                line = document.readline()

            if line.startswith('#index'):
                doc['id'] = line[6:].rstrip()
                line = document.readline()

            if line.startswith('#arnetid'):
                doc['arnetid'] = line[8:].rstrip()
                line = document.readline()

            if line.startswith('#%'):
                references = []
                while line.startswith('#%'):
                    references.append(line[2:].rstrip())
                    line = document.readline()
                doc['references'] = references

            if line.startswith('#!'):
                doc['abstract'] = line[2:].rstrip()
                line = document.readline()

            if line == '\n':
                docs[doc['id']] = doc
                num_docs += 1

                if max_docs and num_docs >= max_docs:
                    break
                doc = {}

            line = document.readline()

    return docs


def parse_to_text_dict(src, max_docs=None):
    """Parses DBLP for documents with an abstract. Combines title with
    abstract into single string

    Args:
        src: path to DBLP file
        max_docs: sets a limit on how many documents to load from file
    Returns:
        text_dict: dictionary mapping from document ids to a string with the
              title and abstract concatenated together
    """
    text_dict = {}

    with open(src, 'r') as document:

        # first line includes the number of citation links
        document.readline()
        line = document.readline()

        num_docs = 0
        while line:

            if line.startswith('#*'):
                title = line[2:-1]
                line = document.readline()

            while not line.startswith('#index'):
                line = document.readline()

            doc_id = line[6:].rstrip()
            line = document.readline()

            while not (line.startswith('#!') or line == '\n'):
                line = document.readline()

            if line.startswith('#!'):
                abstract = line[2:].rstrip()
                text_dict[doc_id] = title + ' ' + abstract
                num_docs += 1
                line = document.readline()

            if max_docs and num_docs >= max_docs:
                break

            line = document.readline()

    return text_dict


def parse_to_references_dict(src, max_docs=None):
    """Parses a DBLP file

    Args:
        src: path to DBLP file
        max_docs: sets a limit on how many documents to load from file
    Returns:
        docs: dictionary mapping from document ids to list of references
              of that document
    """
    docs = {}

    with open(src, 'r') as document:

        # first line includes the number of citation links
        document.readline()
        line = document.readline()

        num_docs = 0
        references = []
        while line:

            if line.startswith('#*'):
                line = document.readline()
            if line.startswith('#@'):
                line = document.readline()
            if line.startswith('#year'):
                line = document.readline()
            if line.startswith('#conf'):
                line = document.readline()
            if line.startswith('#citation'):
                line = document.readline()

            if line.startswith('#index'):
                doc_id = line[6:].rstrip()
                line = document.readline()

            if line.startswith('#arnetid'):
                line = document.readline()

            if line.startswith('#%'):
                references = []
                while line.startswith('#%'):
                    references.append(line[2:].rstrip())
                    line = document.readline()

            if line.startswith('#!'):
                line = document.readline()

            if line == '\n' and references:
                docs[doc_id] = references
                num_docs += 1

                if max_docs and num_docs >= max_docs:
                    break

            line = document.readline()

    return docs
