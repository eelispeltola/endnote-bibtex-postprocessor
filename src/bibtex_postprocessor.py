import logging
from pathlib import Path
import re

import bibtexparser


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def read_bibtex(filepath: Path) -> bibtexparser.Library:
    """
    Read bibtex file into a bibtexparser library.
    """
    with open(filepath) as f:
        bib_str = f.read()

    library = bibtexparser.parse_string(bib_str)

    if len(library.failed_blocks) > 0:
        logger.warning(
            "Some blocks failed to parse. Check the entries of `library.failed_blocks`:"
        )
        logger.warning(library.failed_blocks)
    else:
        logger.info("All blocks parsed successfully")

    return library


def rename_entry_keys(library: bibtexparser.Library) -> bibtexparser.Library:
    """
    For each entry in the library, grab the first author's surname, year, and the first sensible word
    (over two characters and not 'the') from the title, and combine them to generate a new key for that entry.
    """
    for entry in library.entries:
        try:
            year = entry.fields_dict["year"].value
            authors = entry.fields_dict["author"].value.lower()
            first_author_surname = re.split("[,\s]", authors)[0]
            title = entry.fields_dict["title"].value.lower()
        except KeyError:
            raise KeyError(
                f"Missing information (year, author, or title) for entry {entry.key}"
            )

        # Take first sensible word from the title
        split_title = re.split("[:\"'\`,\s]", title)
        first_good_word_in_title = split_title[0]
        for part in split_title:
            if len(part) > 2 and part != "the":
                first_good_word_in_title = part
                break
        entry.key = f"{first_author_surname}{year}{first_good_word_in_title}"

    return library


def write_bibtex(filepath: Path, library: bibtexparser.Library):
    """
    Write bibtexparser library into a bibtex file. Remove extra spacing in front and between entries.

    Parameters:
    - filepath (str): Filepath (with filename) of the new bibtex file.
    - library (bibtexparser.Library): Library to write to file.
    """
    bibtex_format = bibtexparser.BibtexFormat()
    bibtex_format.block_separator = "\n"
    library_str = bibtexparser.write_string(library, bibtex_format=bibtex_format)
    # Match first character that is not \ufeff or whitespace and remove everything before that
    match = re.search(r"[^\ufeff|\s]", library_str)
    if match:
        library_str = library_str[match.start() :]

    with open(filepath, "w") as f:
        f.write(library_str)

    logger.info(f"Wrote fixed bibliography to '{filepath}'")


def postprocess_bibtex(filepath: Path, new_filepath: Path | None = None):
    library = read_bibtex(filepath)
    modded_library = rename_entry_keys(library)
    if not new_filepath:
        # Ensure new file has '.bib' suffix
        new_filepath = filepath.parent / (filepath.name + ".bib")
    write_bibtex(new_filepath, modded_library)


def main():
    fp = Path("/mnt/c/Users/peltole13/Downloads/My EndNote Library.txt")
    postprocess_bibtex(fp)


if __name__ == "__main__":
    main()
