import js from "@eslint/js";
import globals from "globals";
import { defineConfig } from "eslint/config";
import eslintConfigPrettier from "eslint-config-prettier";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs}"],
    plugins: { js },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.browser,
    },
    extends: ["js/recommended"],
  },
  {
    // Global ignores
    ignores: [
      "instance/**",
      ".git/**",
      "node_modules/**",
      ".venv/**",
      ".nox/**",
      ".ruff_cache/**",
      ".pytest_cache/**",
      ".coverage/**",
      "htmlcov/**",
      "**/dist/**",
      "docs/**",
    ],
  },
  eslintConfigPrettier,
]);
