from citemachine import util

class DBLP(object):
    """ 
    Assumed format (V6):
    #* --- paperTitle
    #@ --- Authors
    #year ---- Year
    #conf --- publication venue
    #citation --- citation number (both -1 and 0 means none)
    #index ---- index id of this paper
    #arnetid ---- pid in arnetminer database
    #% ---- the id of references of this paper (there are multiple lines, 
        with each indicating a reference)
    #! --- Abstract

    NOTE: Some fields might be missing! (A good portion of the )
    DATA URL: http://arnetminer.org/citation
    """

    def __init__(self, src):

        self.docs = {}

        with open(src, 'r') as document:

            # first line includes the number of citation links
            line = document.readline().rstrip()
            self.num_citation_links = int(line)

            line = document.readline()
            record = {}
            while line:

                if line.startswith('#*'):
                    record['title'] = line[2:].rstrip()
                    line = document.readline()

                if line.startswith('#@'):
                    record['authors'] = line[2:].rstrip().split(',')
                    line = document.readline()

                if line.startswith('#year'):
                    record['year'] = line[5:].rstrip()
                    line = document.readline()

                if line.startswith('#citation'):
                    record['citation_count'] = int(line[9:].rstrip())
                    line = document.readline()

                if line.startswith('#index'):
                    record['id'] = line[6:].rstrip()
                    line = document.readline()

                if line.startswith('#arnetid'):
                    record['arnetid'] = line[8:].rstrip()
                    line = document.readline()

                if line.startswith('#%'):
                    references = []
                    while line.startswith('#%'):
                        references.append(line[2:].rstrip())
                        line = document.readline()
                    record['references'] = references

                if line.startswith('#!'):
                    record['abstract'] = line[2:].rstrip()
                    line = document.readline()

                if line == '\n':
                    self.docs[record['id']] = record
                    record = {}
                line = document.readline()

    
