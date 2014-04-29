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

def parse_to_doc_dict(src, max_docs=None):
    """Parses a DBLP file

    Args:
        src: path to DBLP file
        max_docs: sets a limit on how many documents to load from file
    Returns:
        docs: dictionary mapping from document ids to document dicts
            docs[doc_id] -> doc, doc[field_name] -> field_value
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
        docs: dictionary mapping from document ids to document reference dicts
            docs[doc_id] -> doc, doc[field_name] -> field_value
            where field_nam can be one of: "authors",
                                           "conference",
                                           "citation_count"
                                           "id",
                                           "references"
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
                line = document.readline()

            if line.startswith('#@'):
                doc['authors'] = line[2:].rstrip().split(',')
                line = document.readline()

            if line.startswith('#year'):
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
                line = document.readline()

            if line.startswith('#%'):
                references = []
                while line.startswith('#%'):
                    references.append(line[2:].rstrip())
                    line = document.readline()
                doc['references'] = references

            if line.startswith('#!'):
                line = document.readline()

            if line == '\n':
                docs[doc['id']] = doc
                num_docs += 1

                if max_docs and num_docs >= max_docs:
                    break
                doc = {}

            line = document.readline()

    return docs