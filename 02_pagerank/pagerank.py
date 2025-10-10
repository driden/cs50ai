import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    corpus = {'1': {'2'}, '2': {'1', '3'}, '3': {'2', '4'}, '4': {'2'}}
    # corpus["1.html"] = set([ "2.html", "3.html"])
    # corpus["2.html"] = set([ "3.html" ])
    # corpus["3.html"] = set([ "2.html" ])
    # print("1.html")
    # print(page_backlinks(corpus, "1.html"))
    # print("2.html")
    # print(page_backlinks(corpus, "2.html"))
    # print("3.html")
    # print(page_backlinks(corpus, "3.html"))
    
    # if len(sys.argv) != 2:
    #     sys.exit("Usage: python pagerank.py corpus")
    # corpus = crawl(sys.argv[1])
    # ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    # print(f"PageRank Results from Sampling (n = {SAMPLES})")
    # for page in sorted(ranks):
    #     print(f"  {page}: {ranks[page]:.4f}")
    # ranks = iterate_pagerank(corpus, DAMPING)
    # print(f"PageRank Results from Iteration")
    # for page in sorted(ranks):
    #     print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


# with probability `dampening_factor` a page decides to navigate to one of its links
# with probability `1 - dampening_factor` a page decides to navigate to a random page
def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Probability of choosing a random page in the corpus
    model = {p: (1 - damping_factor) / len(corpus) for p in corpus}
    page_links = corpus.get(page, set())

    # If current page has no outgoing links then every page gets an equal prob
    if len(page_links) == 0:
        return model

    for link in page_links:
        # Probability of chossing one of the pages linked by current page
        model[link] += damping_factor / len(page_links)
    
    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # This algorithm works by sampling pages and counting how many times they appear in the final result
    ranks ={ page: 0 for page in corpus } 
    page = random.choice(list(corpus))  # random page

    for _ in range(n):
        ranks[page] += 1
        model = transition_model(corpus, page, damping_factor)
        page = random.choices(list(model.keys()), [ p * 100 for p in list(model.values())])[0]
        # page = random.choices(list(model.keys()), weights=model.values(), k=1)[0] # select a new page randomly

    return { page: count / n for page, count in ranks.items() }

def page_backlinks(corpus):
    backlinks = {page: set() for page in corpus}
    for page in corpus:
        if len(corpus[page]) == 0:
            corpus[page] = set(corpus.keys())
        for link in corpus[page]:
            backlinks[link].add(page)
    return backlinks

def should_stop(ranks1, ranks2):
    v1s = list(ranks1.values())
    v2s = list(ranks2.values())

    diffs = [abs(a - b) for (a,b) in list(zip(v1s,v2s))]
    return len([ x for x in diffs if x > 0.001]) == 0

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    ranks = dict()
    backlinks = page_backlinks(corpus)

    # The function should begin by assigning each page a rank of 1 / N, where N is the total number of pages in the corpus.
    for page in corpus:
        ranks[page] = 1 / len(corpus)
    k = (1 - damping_factor) / len(corpus)

    while True:
        new_ranks = copy.deepcopy(ranks)
        for page in corpus:
            # The function should then repeatedly calculate new rank values based on all of the current rank values, according to the PageRank formula
            backlinks_sum = 0
            for backlink in page_backlinks(corpus)[page]:
                # A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself)
                length = min(len(corpus[backlink]), len(corpus))
                backlinks_sum = backlinks_sum + (ranks[backlink] / length)

            new_ranks[page] = k + damping_factor * backlinks_sum 

        else:
            # return of none of the values changed more than 0.001
            if should_stop(ranks, new_ranks):
                return new_ranks
            else:
                ranks = new_ranks



if __name__ == "__main__":
    main()
