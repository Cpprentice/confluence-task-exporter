import sys

from cte.cli_args import get_parser
from cte.config import get_config_entries
from cte.confluence import ConfluenceInterface
from cte.excel import serialize_to_excel


def main():
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    confluence = ConfluenceInterface(*get_config_entries(args.config))
    frame = confluence.get_task_frame(args.page_id)
    serialize_to_excel(frame, args.output)


if __name__ == '__main__':
    main()
