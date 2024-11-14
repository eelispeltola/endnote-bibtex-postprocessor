import logging
from pathlib import Path
import re

import bibtexparser
import click


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# For click
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


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
    For each entry in the library, grab the first author's surname, year, and the first proper word from the title,
    and combine them to generate a new key for that entry.
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

        # Take first sensible word from the title. Discard 'the' and other short words.
        split_title = re.split("[:\"'\`,\s]", title)
        first_good_word_in_title = split_title[0]
        for part in split_title:
            if len(part) > 1 and part not in ["an", "of", "to", "in", "on", "the"]:
                first_good_word_in_title = part
                break
        key_candidate = f"{first_author_surname}{year}{first_good_word_in_title}"
        # Check if key is already in use
        library_keys = [entry.key for entry in library.entries]
        if key_candidate in library_keys:
            logger.debug(
                f"Key '{key_candidate}' already exists in library. Appending entry key with a number."
            )
            i = 2
            while f"{key_candidate}{i}" in library_keys:
                i += 1
            entry.key = f"{key_candidate}{i}"
        else:
            entry.key = key_candidate
    return library


def remove_note_field(library: bibtexparser.Library) -> bibtexparser.Library:
    """
    Remove the 'note' field from each entry. Prevents notes from passing into the final bibliography.
    """
    for entry in library.entries:
        try:
            entry.pop("note")
            logger.debug(f"Removed note from entry {entry.key}")
        except KeyError:
            pass

    return library


def add_braces_to_title_field(library: bibtexparser.Library) -> bibtexparser.Library:
    """
    Add curly braces around all titles, preserving their styling (casing).
    """
    for entry in library.entries:
        try:
            entry.fields_dict["title"].value = (
                "{" + entry.fields_dict["title"].value + "}"
            )
        except KeyError:
            pass
    logger.debug("Modified titles to be encased in curly braces.")

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


def postprocess_bibtex(
    filepath: Path,
    new_filepath: Path | None = None,
    remove_notes: bool = False,
    preserve_titles: bool = False,
):
    library = read_bibtex(filepath)
    modded_library = rename_entry_keys(library)
    if remove_notes:
        modded_library = remove_note_field(modded_library)
    if preserve_titles:
        modded_library = add_braces_to_title_field(modded_library)
    if not new_filepath:
        # Ensure new file has '.bib' suffix and no whitespace
        new_filepath = filepath.parent / (filepath.stem.replace(" ", "_") + ".bib")
        if str(new_filepath) == str(filepath):
            raise FileExistsError(
                "New filepath is same as the old filepath, not overwriting. Try setting a new filename."
            )

    else:
        new_filepath = Path(new_filepath)
        if new_filepath.suffix != ".bib":
            logger.warning(
                "The new filename's suffix is not '.bib', it might not work with your LaTEx compiler."
            )
        if new_filepath.name.find(" ") > 0:
            logger.warning(
                "The new filename has whitespace(s), it might not work with your LaTEx compiler."
            )
    write_bibtex(new_filepath, modded_library)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("bibtex_file", type=click.Path(exists=True))
@click.option(
    "--new-filename", help="If specified, writes file to this filename instead."
)
@click.option(
    "--remove-notes",
    is_flag=True,
    help="Remove the 'note' field from all entries.",
)
@click.option(
    "--preserve-titles",
    is_flag=True,
    help="Add curly braces around all entries' titles, preserving their styling (casing). Note that some publications require specific casing for titles, which this messes with!",
)
def cli(bibtex_file, new_filename, remove_notes, preserve_titles):
    """
    Postprocess BIBTEX_FILE so that entry keys are written as
    [first author's surname][year][first longer word in title],
    and write the result in a new file. The first longer word is at least 2
    characters long and is not any of the following: "an", "of", "to", "in",
    "on", or "the". Optionally remove notes and add braces to titles.
    """
    bibtex_file = Path(bibtex_file)
    try:
        postprocess_bibtex(bibtex_file, new_filename, remove_notes, preserve_titles)
    except Exception as e:
        logger.error(f"Error: {e}")
