/**
 * Facilitate autocomplete suggestions for a text input.
 *
 * Opens an interface for suggesting input values when a user interacts
 * with a form input. The interface can be navigated using the tab,
 * arrow, and enter keys, and attempts to be as intuitive as possible.
 */

import { sendPostRequest } from "dry-foundation/requests";

/**
 * Test whether `target` starts with `prefix` (case-sensitive).
 *
 * @param {string} prefix - The candidate prefix.
 * @param {string} target - The string being tested.
 * @returns {boolean} Whether `target` begins with `prefix`.
 */
function isAnchoredMatch(prefix, target) {
  return target.startsWith(prefix);
}

/**
 * Test whether `target` contains `substring` anywhere (case-sensitive).
 *
 * @param {string} substring - The candidate substring.
 * @param {string} target - The string being tested.
 * @returns {boolean} Whether `target` contains `substring`.
 */
function isContainedMatch(substring, target) {
  return target.includes(substring);
}

/**
 * A dropdown box displaying/managing autocomplete suggestions.
 *
 * Each instance manages exactly one input element and creates its own
 * suggestion box in the DOM; use a separate `AutocompleteBox` per input
 * that needs autocomplete behavior.
 *
 * Usage protocol: after construction, call `postRequest` to fetch the
 * full set of candidate suggestions from the server (via
 * `dry-foundation/requests`'s `sendPostRequest`). That response is
 * cached on the instance and filtered client-side against the user's
 * input on every keystroke — `postRequest` does not need to be called
 * again as the user types.
 *
 * Keyboard controls, once the box is open:
 * - `ArrowUp`/`ArrowDown`: move the highlighted ("active") suggestion.
 * - `Tab`/`Shift+Tab`: same as arrow down/up, respectively.
 * - `Enter`: select the active suggestion (or close with no
 *   selection, if none is active).
 * - `ArrowRight`: select the active suggestion and allow further editing
 *   of the selection text.
 *
 * Call `release()` when the input element is being removed from the
 * DOM or no longer needs autocomplete behavior to avoid leaking event
 * listeners.
 */
class AutocompleteBox {
  defaultBoxSize = 10;
  defaultBoxStartIndex = 0;
  boxClassName = "autocomplete-box";

  /**
   * Create the autocomplete box for a given input element.
   *
   * @param {Element} inputElement - The input element that will
   *     trigger and receive autocomplete suggestions.
   */
  constructor(inputElement) {
    this.inputElement = inputElement;
    this.boxSize = this.defaultBoxSize;
    this.boxStartIndex = this.defaultBoxStartIndex;
    this.boxElement = null;
    this.boxSuggestions = [];
    this.matches = [];
    this.response = [];
    this.currentFocus = -1;
    // Store bound references so they can be removed
    this._handleInput = this.update.bind(this);
    this._handleKeydown = this.#handleKeydown.bind(this);
    // Bind the update method to any input action
    this.inputElement.removeEventListener("input", this._handleInput);
    this.inputElement.addEventListener("input", this._handleInput);
  }

  /**
   * Tear down this instance's event listeners.
   *
   * Closes the box (if open) and removes the `input` listener bound in
   * the constructor. Call this before discarding an `AutocompleteBox`
   * instance (e.g., when its input element is removed from the page)
   * to avoid leaking event listeners.
   */
  release() {
    this.close();
    this.inputElement.removeEventListener("input", this._handleInput);
  }

  /**
   * The ending index (exclusive) of the currently visible suggestion window.
   *
   * @returns {number}
   */
  get boxEndIndex() {
    return this.boxStartIndex + this.boxSize;
  }

  /**
   * Cache the full set of candidate suggestions returned by the server.
   *
   * @param {string[]} response - The list of candidate suggestion
   *     strings, to be filtered client-side against user input.
   */
  loadResponse(response) {
    this.response = response;
  }

  /**
   * Fetch the full set of candidate suggestions from the server.
   *
   * The response is cached via `loadResponse` and does not need to be
   * re-fetched as the user types; matching against typed input happens
   * client-side using the cached response.
   *
   * @param {string} endpoint - The URL to POST to.
   * @param {*} rawData - The request payload, passed through to
   *     `sendPostRequest`.
   */
  postRequest(endpoint, rawData) {
    sendPostRequest(endpoint, rawData, this.loadResponse.bind(this));
  }

  /**
   * Handle an `input` event on the associated input element.
   *
   * Refreshes the list of matches for the current input value, and
   * opens/refreshes or closes the suggestion box as appropriate.
   */
  update() {
    const userInput = this.inputElement.value;
    if (this.#needsRefresh(userInput)) {
      if (!this.boxElement) {
        this.open();
      }
      this.refresh();
    } else {
      this.close();
    }
  }

  /**
   * Create the suggestion box element and insert it into the DOM.
   *
   * The box is appended as a sibling of the input element (inside the
   * input's parent) and keyboard navigation is bound for as long as
   * the box remains open.
   */
  open() {
    this.boxElement = document.createElement("div");
    this.boxElement.className = this.boxClassName;
    this.inputElement.parentElement.appendChild(this.boxElement);
    this.#bindKeyboardAction();
  }

  /**
   * Close the suggestion box (and unbind its keyboard navigation).
   *
   * Safe to call whether or not the box is currently open.
   */
  close() {
    this.clear();
    if (this.boxElement) {
      this.boxElement.remove();
    }
    this.boxElement = null;
    this.#unbindKeyboardAction();
  }

  /**
   * Clear and repopulate the suggestion box using the current matches.
   */
  refresh() {
    this.clear();
    this.populate();
  }

  /**
   * Clear and repopulate the suggestion box using the current matches.
   */
  clear() {
    this.boxSuggestions.forEach((suggestion) => suggestion.remove());
    this.boxSuggestions = [];
  }

  /**
   * Render the current window of `matches` (per `boxStartIndex`/
   * `boxEndIndex`) as suggestion elements inside the box, and bind
   * mouse interaction to each one.
   *
   * Suggestion text is set via `textContent`, so it is always treated
   * as plain text (not HTML), even if it contains characters like `<`
   * or `&`.
   */
  populate() {
    this.#setBoxRange();
    for (let i = this.boxStartIndex; i < this.boxEndIndex; i++) {
      const suggestionElement = document.createElement("div");
      suggestionElement.className = "item";
      suggestionElement.textContent = this.matches[i];
      this.boxElement.appendChild(suggestionElement);
    }
    this.boxSuggestions = Array.from(
      this.boxElement.querySelectorAll("div.item"),
    );
    this.#bindMouseAction();
  }

  /**
   * Select a suggestion (fill in the input text and then close the box).
   *
   * @param {Element|null} suggestion - The suggestion element to
   *     select, or `null` to close the box without filling the input
   *     (e.g., when Enter is pressed with no suggestion highlighted).
   * @param {boolean} [advance=true] - Whether to move focus to the
   *     next input in the form after selecting.
   */
  select(suggestion, advance = true) {
    if (suggestion !== null) {
      this.fill(suggestion);
    }
    this.close();
    if (advance) {
      this.advanceFocus();
    }
  }

  /**
   * Populate the input element text using the chosen suggestion.
   */
  fill(suggestion) {
    this.inputElement.value = suggestion.textContent;
  }

  /**
   * Shift focus to the next input on the same form element.
   *
   * If this is the last input on the form, this does nothing.
   */
  advanceFocus() {
    const formInputs = Array.from(
      this.inputElement.closest("form").querySelectorAll("input"),
    );
    const nextInputIndex = formInputs.indexOf(this.inputElement) + 1;
    formInputs[nextInputIndex]?.focus();
  }

  #needsRefresh(userInput) {
    // Check if the list of matches needs to be refreshed
    this.refreshMatches(userInput);
    const matchCount = this.matches.length;
    const matchIsUserInput = matchCount === 1 && userInput === this.matches[0];
    return !(matchCount < 1 || matchIsUserInput || !userInput);
  }

  /**
   * Refresh autocomplete suggestions using the POST response.
   *
   * Resets the box's scroll window and highlighted suggestion, then
   * recomputes `matches` against the cached `response`, preferring
   * anchored (prefix) matches before contained (substring) matches.
   *
   * @param {string} userInput - The input element's current value.
   */
  refreshMatches(userInput) {
    this.matches = [];
    this.boxStartIndex = this.defaultBoxStartIndex;
    this.currentFocus = -1;
    this.#testMatches(userInput, isAnchoredMatch);
    this.#testMatches(userInput, isContainedMatch);
  }

  #testMatches(userInput, testFunction) {
    // Add responses matching the user input to the set of matching suggestions
    for (const responseSuggestion of this.response) {
      // Test (lowercase) match status and if already recorded
      const lowercaseSuggestion = responseSuggestion.toLowerCase();
      const lowercaseInput = userInput.toLowerCase();
      const isMatch = testFunction(lowercaseInput, lowercaseSuggestion);
      const isNotYetIncluded = !this.matches.includes(responseSuggestion);
      if (isMatch && isNotYetIncluded) {
        // Add new matches to the list of suggestions
        this.matches.push(responseSuggestion);
      }
    }
  }

  #setBoxRange() {
    // Set the range of the autocomplete box
    this.boxSize = Math.min(this.matches.length, this.defaultBoxSize);
    if (this.boxEndIndex > this.matches.length) {
      // Box overextends available matches; reset the starting point
      this.boxStartIndex = this.matches.length - this.boxSize;
    }
  }

  #bindMouseAction() {
    // Bind mouse action functionality to each suggestion
    this.boxSuggestions.forEach((suggestion) => {
      suggestion.addEventListener("mousedown", (event) => {
        // Prevent "premature" blurring
        event.preventDefault();
      });
      suggestion.addEventListener("click", () => this.select(suggestion));
    });
  }

  #bindKeyboardAction() {
    this.currentFocus = -1;
    this.inputElement.addEventListener("keydown", this._handleKeydown);
  }

  #handleKeydown(event) {
    switch (event.key) {
      case "Enter":
        event.preventDefault();
        this.#selectActiveSuggestion();
        break;
      case "Tab":
        event.preventDefault();
        event.shiftKey ? this.#moveCursorUp() : this.#moveCursorDown();
        break;
      case "ArrowUp":
        event.preventDefault();
        this.#moveCursorUp();
        break;
      case "ArrowDown":
        event.preventDefault();
        this.#moveCursorDown();
        break;
      case "ArrowRight":
        this.#selectActiveSuggestion();
        break;
    }
  }

  #selectActiveSuggestion() {
    // Select the highlighted 'active' suggestion
    const notOnText = this.currentFocus !== -1;
    const suggestion = notOnText
      ? this.boxElement.querySelector("div.item.active")
      : null;
    this.select(suggestion);
  }

  #moveCursorUp() {
    // Move the cursor up (depending on the box window)
    const notOnText = this.currentFocus > -1;
    const atTop = this.currentFocus === 0;
    const matchesRemainAbove = this.boxStartIndex > 0;
    if (notOnText) {
      atTop && matchesRemainAbove ? this.boxStartIndex-- : this.currentFocus--;
    }
    this.refresh();
    this.#highlight();
  }

  #moveCursorDown() {
    // Move the cursor down (depending on the box window)
    const notAtBottom = this.currentFocus < this.boxSize - 1;
    const atBottom = this.currentFocus === this.boxSize - 1;
    const matchesRemainBelow = this.boxEndIndex < this.matches.length;
    if (notAtBottom) {
      this.currentFocus++;
    } else if (atBottom && matchesRemainBelow) {
      this.boxStartIndex++;
    }
    this.refresh();
    this.#highlight();
  }

  #highlight() {
    // Highlight the suggestion as the 'active' suggestion
    this.boxSuggestions.forEach((suggestion) => {
      suggestion.classList.remove("active");
    });
    if (this.currentFocus >= 0) {
      this.boxSuggestions[this.currentFocus]?.classList.add("active");
    }
  }

  #unbindKeyboardAction() {
    // Unbind keyboard action functionality from all suggestions
    this.inputElement.removeEventListener("keydown", this._handleKeydown);
  }
}

export { AutocompleteBox };
