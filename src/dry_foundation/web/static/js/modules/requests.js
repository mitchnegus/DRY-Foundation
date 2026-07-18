/**
 * Provide standardized utility functions for handling network communications.
 */

/**
 * Send an HTTP POST request with a JSON payload using the native Fetch API.
 *
 * @param {string} endpoint - The target URL or API route for the request.
 * @param {Object} rawData - The JavaScript object containing the payload
 *     to payload data.
 * @param {Function} [action=() => {}] - Optional callback function executed
 *     on a successful response. Receives the parsed JSON response object as
 *     its sole parameter.
 * @returns {void}
 */
function sendPostRequest(endpoint, rawData, action = () => {}) {
  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json; charset=UTF-8",
    },
    body: JSON.stringify(rawData),
  })
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then((data) => {
      action(data);
    })
    .catch((error) => {
      console.log("There was an error in the request.", error);
    });
}

export { sendPostRequest };
