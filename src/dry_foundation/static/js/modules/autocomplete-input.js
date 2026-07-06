/*
 * Execute the autocomplete interface when using an input element.
 *
 * Opens an interface for suggesting input values when a user interacts
 * with a form input. The interface can be navigated using the tab and
 * enter keys, and attempts to be as intuitive as possible.
 */

import { sendPostRequest } from "dry-foundation/requests";

function isAnchoredMatch(prefix, target) {
  return target.startsWith(prefix);
}

function isContainedMatch(substring, target) {
  return target.includes(substring);
}

class AutocompleteBox {
  // A box for displaying autocomplete suggestions
  defaultBoxSize = 10;
  defaultBoxStartIndex = 0;
  boxClassName = "autocomplete-box";

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

  release() {
    this.close();
    this.inputElement.removeEventListener("input", this._handleInput);
  }

  get boxEndIndex() {
    return this.boxStartIndex + this.boxSize;
  }

  loadResponse(response) {
    this.response = response;
  }

  postRequest(endpoint, rawData) {
    // Execute a POST request to find matches
    sendPostRequest(endpoint, rawData, this.loadResponse.bind(this));
  }

  update() {
    // Update the box (opening or closing it if necessary)
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

  open() {
    // Open the autocomplete box
    this.boxElement = document.createElement("div");
    this.boxElement.className = this.boxClassName;
    this.inputElement.parentElement.appendChild(this.boxElement);
    this.#bindKeyboardAction();
  }

  close() {
    // Close the autocomplete box
    this.clear();
    if (this.boxElement) {
      this.boxElement.remove();
    }
    this.boxElement = null;
    this.#unbindKeyboardAction();
  }

  refresh() {
    // Refresh the box by clearing old suggestions and populating with new ones
    this.clear();
    this.populate();
  }

  clear() {
    // Clear the suggestions in the autocomplete box
    this.boxSuggestions.forEach((suggestion) => suggestion.remove());
    this.boxSuggestions = [];
  }

  populate() {
    // Populate the autocomplete box with suggestions
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

  select(suggestion, advance = true) {
    // Select a suggestion from the list
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

  advanceFocus() {
    // Shift the focus to the next input element
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
