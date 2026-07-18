/**
 * Facilitate the replacement of form values with suggestions.
 */

/**
 * A class for replacing elements of a form with suggested values.
 *
 * Each instance manages exactly one suggestion element. To wire up
 * multiple suggestions on a page, create a separate `SuggestionSelector`
 * (or subclass instance) for each one.
 *
 * Markup contract: the suggestion element is expected to live inside a
 * form field container matching `.form-field.suggestable`, and that
 * container must contain the `<input>` whose value should be replaced.
 */
class SuggestionSelector {
  /**
   * Create the suggestion selector.
   *
   * @param {JQuery} $suggestion - An single suggestion element. Its text
   *     will be used (via `getSuggestionText`) to determine the value
   *     used to replace the associated input's value when clicked.
   */
  constructor($suggestion) {
    this.$suggestion = $suggestion;
    this.$suggestion.on("click", () => {
      this.#replaceValue();
    });
  }

  /**
   * Replace the value of the input field (by ID) with the suggested value.
   *
   * The associated input is found by looking up from the suggestion
   * element to its nearest `.form-field.suggestable` ancestor, then
   * finding the `<input>` within it.
   */
  #replaceValue() {
    const $formField = this.$suggestion.closest(".form-field.suggestable");
    const $input = $formField.find("input");
    $input.val(this.getSuggestionText());
  }

  /**
   * Get the text of the suggestion from the suggestion object.
   *
   * Subclasses can override this to transform the suggestion's raw
   * text (e.g., stripping currency formatting) before it's used.
   */
  getSuggestionText() {
    return this.$suggestion.text();
  }
}

export { SuggestionSelector };
