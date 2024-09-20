from argparse import ArgumentParser


def get_parser():
    parser = ArgumentParser()
    parser.add_argument('page_id', nargs='+', help='specify at least one page id to export todos from')
    parser.add_argument('--config', metavar='<config-file-path>', default='cte.toml',
                        help='specify the file to load the config from')
    parser.add_argument('--output', metavar='<output-file-path>', default='tasks.xlsx',
                        help='specify the target file to create from the task list')

    return parser
