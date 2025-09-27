import os
import random
import re
import sys

from icdiff import start

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


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


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    page_ranks_result = init_pages_dict_with_corpus(corpus)

    all_pages_p = (1 - damping_factor) / len(page_ranks_result)
    current_page_neighbours_p = len(corpus[page]) / damping_factor + all_pages_p

    for a_page in page_ranks_result:
        if a_page in corpus[page]:
            page_ranks_result[a_page] = current_page_neighbours_p
        else:
            page_ranks_result[a_page] = all_pages_p

    print(page_ranks_result)
    return page_ranks_result


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_ranks_result = init_pages_dict_with_corpus(corpus)
    pages: list[str] = [key for key in page_ranks_result.keys()]
    start_page = random.choice(pages)
    transition = transition_model(corpus, start_page, damping_factor)

    for i in range(n):
        next_page = random_page_by_weights(transition)
        page_ranks_result[next_page] += 1
        transition = transition_model(corpus, next_page, damping_factor)

    for _, page in enumerate(pages):
        page_ranks_result[page] = page_ranks_result[page] / n

    return page_ranks_result


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_ranks_result = init_pages_dict_with_corpus(corpus)
    default_value = 1 / len(page_ranks_result.keys())
    page_ranks_result = init_pages_dict_with_corpus(corpus, default_value)

    pages: list[str] = [key for key in page_ranks_result.keys()]

    page_ranks_result_new = calc_new_ranks(pages, damping_factor, page_ranks_result, corpus)

    iterations_count_limit = 50000
    iterations_count = 0

    while (not is_deltas_match_precision(page_ranks_result, page_ranks_result_new, 0.001)
           and iterations_count < iterations_count_limit):
        iterations_count += 1
        page_ranks_result = page_ranks_result_new
        page_ranks_result_new = calc_new_ranks(pages, damping_factor, page_ranks_result, corpus)
    return page_ranks_result_new


def is_deltas_match_precision(first_page_ranks_result: dict[str, float],
                              second_page_ranks_result: dict[str, float],
                              precision: float):
    for page in first_page_ranks_result.keys():
        if abs(first_page_ranks_result[page] - second_page_ranks_result[page]) > precision:
            return False

    return True


def calc_new_ranks(pages: list[str], damping_factor: float,
                   current_page_ranks_result: dict[str, float], corpus: dict[str, set[str]]):
    page_ranks_result_new = dict()
    for page in pages:
        p1 = (1 - damping_factor) / len(pages)
        p2 = sum([current_page_ranks_result[pge] / len(corpus[pge])
                  for pge in pages if pge != page and page in corpus[pge]])
        page_ranks_result_new[page] = p1 + damping_factor * p2

    return page_ranks_result_new


def init_pages_dict_with_corpus(corpus: dict[str, set[str]], default_value: float = 0.0) -> dict[str, float]:
    return {key: default_value for key in (set(corpus.keys()) | {page for pages in corpus.values() for page in pages})}


def random_page_by_weights(transition: dict[str, float]) -> str:
    return random.choices(
        population=[page for page in transition.keys()], weights=[weight for weight in transition.values()], k=1)[0]


if __name__ == "__main__":
    main()
