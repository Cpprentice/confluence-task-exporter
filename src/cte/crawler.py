import argparse
import re
import shelve
import sys

from cte import ConfluenceInterface
from cte.config import get_config_entries


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='<config-file-path>', default='cte.toml',
                        help='specify the file to load the config from')
    parser.add_argument('--space', metavar='<space-key>', action='append',
                        help='specify the confluence space to crawl. You can pass this multiple times')
    parser.add_argument('--limit', metavar='<limit>', type=int, default=50,
                        help='Specify how many pages to process in a single run. '
                             'Following runs will continue where the previous one stopped!')

    mutually_exclusive_group = parser.add_mutually_exclusive_group(required=True)
    mutually_exclusive_group.add_argument('--search', metavar='<search-expression>',
                                          help='regular expression to search for in confluence')
    mutually_exclusive_group.add_argument('--list-spaces', action='store_true',
                                          help='Print a list of available spaces and exit')
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])
    confluence = ConfluenceInterface(*get_config_entries(args.config))
    available_spaces = confluence.get_spaces()

    if args.list_spaces:
        print('Available spaces:')
        print('\n'.join(available_spaces))
        sys.exit(0)

    requested_spaces = set(args.space)
    invalid_spaces = requested_spaces - available_spaces
    if invalid_spaces:
        parser.error(f'The following spaces are not available: {", ".join(invalid_spaces)}')

    expr = re.compile(args.search, re.IGNORECASE)
    processed_count = 0

    with shelve.open('crawl_cache') as general_cache:
        if args.search not in general_cache:
            general_cache[args.search] = {}
        cache = general_cache[args.search]

        if 'visited' not in cache:
            cache['visited'] = set()
        visited = cache['visited']

        for space_key in args.space:
            if processed_count >= args.limit:
                break
            page_ids = confluence.get_page_list_for_space(space_key)
            for page_id in page_ids:
                if processed_count >= args.limit:
                    break
                if (space_key, page_id) not in visited:
                    body = confluence.get_page_body(page_id)
                    match = re.search(expr, body)
                    if match is not None:
                        start = max(match.regs[0][0] - 30, 0)
                        end = min(match.regs[0][1] + 30, match.endpos)
                        print(f'Matched term in "{body[start:end]}":', confluence.make_heading_link({"id": page_id}, None))
                    else:
                        visited.add((space_key, page_id))
                    processed_count += 1

        if processed_count < args.limit:
            print('Completed all pages')
        else:
            print(f'Processed {processed_count} pages this run')

        # write back to cache
        # cache['visited'] = visited
        general_cache[args.search] = cache


if __name__ == '__main__':
    main()
