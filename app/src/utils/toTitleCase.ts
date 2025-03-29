/* To Title Case © 2018 David Gouch | https://github.com/gouch/to-title-case */

declare global {
  interface String {
    toTitleCase(): string;
  }
}

// eslint-disable-next-line no-extend-native
String.prototype.toTitleCase = function (): string {
  'use strict';
  const smallWords = /^(a|an|and|as|at|but|by|en|for|if|in|nor|of|or|per|the|to|v\.?|vs\.?|via|le|la|les|du|de|des|un|une|ou|où|or|ni|car|sans|avec|ce|ces|cet|cette|d|l|et|à|dans|nos|vos|notre|votre|mon|ton|ta|ma|tes|mes|son|sa|ses|pour|se|par|sur)$/i;
  const upperWords = /^(FC|US|AG)$/i;
  const alphanumericPattern = /([A-Za-z0-9\u00C0-\u00FF])/;
  const wordSeparators = /([ :’'–—-])/;

  return this.split(wordSeparators)
    .map((current: string, index: number, array: string[]): string => {
      if (current.search(upperWords) > -1) {
        return current.toUpperCase();
      }
      if (
        /* Check for small words */
        current.search(smallWords) > -1 &&
        /* Skip first and last word */
        index !== 0 &&
        index !== array.length - 1 &&
        /* Ignore title end and subtitle start */
        array[index - 3] !== ':' &&
        array[index + 1] !== ':' &&
        /* Ignore small words that start a hyphenated phrase */
        (array[index + 1] !== '-' ||
          (array[index - 1] === '-' && array[index + 1] === '-'))
      ) {
        return current.toLowerCase();
      }

      /* Ignore intentional capitalization */
      if (current.substr(1).search(/[A-Z]|\./) > -1) {
        return current;
      }

      /* Ignore URLs */
      if (array[index + 1] === ':' && array[index + 2] !== '') {
        return current;
      }

      /* Capitalize the first letter */
      return current.replace(alphanumericPattern, (match: string): string => {
        return match.toUpperCase();
      });
    })
    .join('');
};
