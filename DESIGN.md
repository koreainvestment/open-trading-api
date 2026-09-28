# Open Trading API Design Contract

## Product character
- Treat the strategy builder and backtester as analyst workstations, not marketing pages.
- Prioritize evidence, risk visibility, reproducible inputs, and clear execution state.
- Never imply guaranteed returns or hide whether an action targets paper or live trading.

## Visual language
- Use the existing KIS blue #245bee as the primary action color.
- Preserve the Korean market convention: profit/up is red, loss/down is blue, neutral is gray.
- Reuse the existing slate surfaces, 8-12px radii, compact cards, tabular numerals, and light/dark themes.
- Keep charts and tables information-dense with stable labels and visible units.

## Interaction and states
- Every network or long-running action must expose loading, empty, error, and retry states.
- Live-order actions must be visually distinct from analysis, simulation, and paper trading.
- Destructive or real-order actions require explicit confirmation and must not be triggered by background validation.
- Keyboard focus must stay visible; icon-only buttons need accessible labels.
- On narrow screens controls may wrap, but primary inputs, warnings, and results must not overlap or clip.

## Verification
- Run ESLint and the Next.js production build for each frontend after UI changes.
- Check critical screens at desktop and mobile widths when a browser runtime is available.
- Verify Korean labels, profit/loss colors, empty/error states, and chart tooltips.
