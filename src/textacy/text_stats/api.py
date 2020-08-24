"""
Text Statistics
---------------

Compute various basic counts and readability statistics for documents.
"""
import logging
from typing import Tuple

from cytoolz import itertoolz
from spacy.tokens import Doc

from .. import extract
from . import basics, readability


LOGGER = logging.getLogger(__name__)


class TextStats:
    """
    Class to compute a variety of basic counts and readability statistics for a given
    document. For example:

    .. code-block:: pycon

        >>> text = next(textacy.datasets.CapitolWords().texts(limit=1))
        >>> doc = textacy.make_spacy_doc(text)
        >>> ts = TextStats(doc)

    Args:
        doc: A text document tokenized and (optionally) sentence-segmented by spaCy.
    """

    def __init__(self, doc: Doc):
        self.lang = doc.vocab.lang
        self.words = tuple(
            extract.words(doc, filter_punct=True, filter_stops=False, filter_nums=False)
        )
        self.n_sents = basics.n_sents(doc)
        self._n_words = None
        self._n_unique_words = None
        self._n_long_words = None
        self._n_chars_per_word = None
        self._n_chars = None
        self._n_syllables_per_word = None
        self._n_syllables = None
        self._n_monosyllable_words = None
        self._n_polysyllable_words = None

    @property
    def n_words(self) -> int:
        """
        Number of words in document.

        See Also:
            :func:`basics.n_words()`
        """
        if self._n_words is None:
            self._n_words = basics.n_words(self.words)
        return self._n_words

    @property
    def n_unique_words(self) -> int:
        """
        Number of *unique* words in document.

        See Also:
            :func:`basics.n_unique_words()`
        """
        if self._n_unique_words is None:
            self._n_unique_words = basics.n_unique_words(self.words)
        return self._n_unique_words

    @property
    def n_long_words(self) -> int:
        """
        Number of long words in document.

        See Also:
            :func:`basics.n_long_words()`
        """
        # TODO: should we vary char threshold by lang?
        if self._n_long_words is None:
            self._n_long_words = basics.n_long_words(
                self.n_chars_per_word, min_n_chars=7,
            )
        return self._n_long_words

    @property
    def n_chars_per_word(self) -> Tuple[int, ...]:
        """
        Number of characters for each word in document.

        See Also:
            :func:`basics.n_chars_per_word()`
        """
        if self._n_chars_per_word is None:
            self._n_chars_per_word = basics.n_chars_per_word(self.words)
        return self._n_chars_per_word

    @property
    def n_chars(self) -> int:
        """
        Total number of characters in document.

        See Also:
            :func:`basics.n_chars()`
        """
        if self._n_chars is None:
            self._n_chars = basics.n_chars(self.n_chars_per_word)
        return self._n_chars

    @property
    def n_syllables_per_word(self) -> Tuple[int, ...]:
        """
        Number of syllables for each word in document.

        See Also:
            :func:`basics.n_syllables_per_word()`
        """
        if self._n_syllables_per_word is None:
            self._n_syllables_per_word = basics.n_syllables_per_word(
                self.words, self.lang,
            )
        return self._n_syllables_per_word

    @property
    def n_syllables(self) -> int:
        """
        Total number of syllables in document.

        See Also:
            :func:`basics.n_syllables()`
        """
        if self._n_syllables is None:
            self._n_syllables = basics.n_syllables(self.n_syllables_per_word)
        return self._n_syllables

    @property
    def n_monosyllable_words(self) -> int:
        """
        Number of monosyllobic words in document.

        See Also:
            :func:`basics.n_monosyllable_words()`
        """
        if self._n_monosyllable_words is None:
            self._n_monosyllable_words = basics.n_monosyllable_words(
                self.n_syllables_per_word,
            )
        return self._n_monosyllable_words

    @property
    def n_polysyllable_words(self) -> int:
        """
        Number of polysyllobic words in document.

        See Also:
            :func:`basics.n_polysyllable_words()`
        """
        # TODO: should we vary syllable threshold by lang?
        if self._n_polysyllable_words is None:
            self._n_polysyllable_words = basics.n_polysyllable_words(
                self.n_syllables_per_word, min_n_syllables=3,
            )
        return self._n_polysyllable_words

    @property
    def automated_readability_index(self) -> float:
        return readability.automated_readability_index(
            self.n_chars, self.n_words, self.n_sents,
        )

    @property
    def automatic_arabic_readability_index(self) -> float:
        if self.lang != "ar":
            LOGGER.warning(
                "doc lang = '%s', but automatic arabic readability index is meant "
                "for use on Arabic-language texts, only"
            )
        return readability.automated_readability_index(
            self.n_chars, self.n_words, self.n_sents,
        )

    @property
    def coleman_liau_index(self) -> float:
        return readability.coleman_liau_index(self.n_chars, self.n_words, self.n_sents)

    @property
    def flesch_kincaid_grade_level(self) -> float:
        return readability.flesch_kincaid_grade_level(
            self.n_syllables, self.n_words, self.n_sents,
        )

    @property
    def flesch_reading_ease(self) -> float:
        return readability.flesch_reading_ease(
            self.n_syllables, self.n_words, self.n_sents, lang=self.lang
        )

    @property
    def gulpease_index(self) -> float:
        if self.lang != "it":
            LOGGER.warning(
                "doc lang = '%s', but gulpease index is meant for use on "
                "Italian-language texts, only"
            )
        return readability.gulpease_index(self.n_chars, self.n_words, self.n_sents)

    @property
    def gunning_fog_index(self) -> float:
        return readability.gunning_fog_index(
            self.n_words, self.n_polysyllable_words, self.n_sents,
        )

    @property
    def lix(self) -> float:
        return readability.lix(self.n_words, self.n_long_words, self.n_sents)

    @property
    def mu_legibility_index(self) -> float:
        if self.lang != "es":
            LOGGER.warning(
                "doc lang = '%s', but mu legibility index is meant for use on "
                "Spanish-language texts, only"
            )
        return readability.mu_legibility_index(self.words)

    @property
    def perspicuity_index(self) -> float:
        if self.lang != "es":
            LOGGER.warning(
                "doc lang = '%s', but perspicuity index is meant for use on "
                "Spanish-language texts, only"
            )
        return readability.perspicuity_index(
            self.n_words, self.n_syllables, self.n_sents,
        )

    @property
    def smog_index(self) -> float:
        return readability.smog_index(self.n_polysyllable_words, self.n_sents)

    @property
    def wiener_sachtextformel(self) -> float:
        if self.lang != "es":
            LOGGER.warning(
                "doc lang = '%s', but wiener sachtextformel is meant for use on "
                "German-language texts, only"
            )
        return readability.wiener_sachtextformel(
            self.n_words,
            self.n_polysyllable_words,
            self.n_monosyllable_words,
            self.n_long_words,
            self.n_sents,
            variant=1,
        )