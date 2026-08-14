```markdown
# Design System Strategy: The Empathetic Intelligence

## 1. Overview & Creative North Star
The Creative North Star for this design system is **"The Digital Sanctuary."** In the context of Indian Sign Language (ISL) translation, the UI must transition from being a "tool" to becoming an invisible, supportive environment. 

We reject the "generic SaaS" aesthetic of heavy borders and rigid grids. Instead, we embrace **Soft Structuralism**. This approach uses intentional asymmetry, overlapping layers, and high-contrast typography scales to create a premium, editorial feel. We move away from the "template" look by treating the interface as a living, breathing space where AI technology feels deeply human-centric, fluid, and profoundly accessible.

## 2. Color Theory & Tonal Depth
This system is built on a foundation of "Trustworthy Blues" and "Supportive Accents," utilizing Material Design logic to create a sophisticated, layered atmosphere.

### The Palette
*   **Primary Core (`#00478d`):** Our "Trustworthy Blue." Use this for authoritative actions and key brand moments.
*   **Secondary Support (`#006a63`):** A soft teal representing growth and communication.
*   **Tertiary Accents (`#572f9a`):** A sophisticated purple for AI-driven insights and "magical" features.
*   **Neutral Surfaces (`#f7f9fb` to `#ffffff`):** A range of cool whites and soft greys that prevent eye fatigue during long signing sessions.

### Critical Rules for Visual Polish
*   **The "No-Line" Rule:** 1px solid borders are strictly prohibited for sectioning. Boundaries must be defined solely through background color shifts. For example, a `surface_container_low` section sitting on a `surface` background provides all the definition needed without the "cheap" look of outlines.
*   **Surface Hierarchy & Nesting:** Treat the UI as stacked sheets of fine paper. An outer container uses `surface_container`, while nested inner cards should step up to `surface_container_lowest` (pure white) to create a natural, "lifted" focal point.
*   **The "Glass & Gradient" Rule:** To signal "tech-forward" intelligence, floating elements (like camera controls) should use Glassmorphism. Use semi-transparent `surface` colors with a `backdrop-blur` effect. 
*   **Signature Textures:** For Hero sections or Primary CTAs, use a subtle linear gradient transitioning from `primary` to `primary_container`. This adds a "soul" to the UI that flat hex codes cannot achieve.

## 3. Typography: The Editorial Voice
We utilize a dual-font pairing to balance authority with extreme legibility.

*   **Display & Headlines (Manrope):** We use Manrope for its modern, geometric construction. Its wide apertures ensure that even at large scales (`display-lg`: 3.5rem), the brand feels open and approachable.
*   **Title, Body, & Labels (Inter):** Inter is our workhorse. Specifically chosen for its tall x-height, it ensures maximum readability for ISL glossaries and instructional text.
*   **Hierarchy as Identity:** Use `headline-lg` (2rem) in close proximity to `body-md` (0.875rem) to create a high-contrast, editorial rhythm. This "Large-and-Small" approach breaks the monotony of standard web layouts.

## 4. Elevation & Depth
We convey importance through **Tonal Layering** and ambient physics rather than artificial shadows.

*   **The Layering Principle:** Depth is achieved by stacking. Place a `surface_container_lowest` card on a `surface_container_low` background. The slight delta in brightness creates a sophisticated, "soft-touch" lift.
*   **Ambient Shadows:** When a shadow is necessary for floating elements (e.g., a "Camera On" toggle), it must be extra-diffused. 
    *   *Spec:* Blur: 24px-48px | Opacity: 4%-6% | Color: Tinted with `on_surface` (never pure black).
*   **The "Ghost Border" Fallback:** For accessibility in input fields, use a "Ghost Border"—the `outline_variant` token at 15% opacity. This provides a hint of structure without cluttering the visual field.
*   **Glassmorphism Depth:** Use `surface_variant` at 70% opacity with a 12px blur for overlay panels. This ensures the user never loses context of the video feed behind the UI.

## 5. Components
Each component must feel "tactile" and responsive, respecting the **Roundedness Scale** (default: `0.5rem`).

*   **Action Buttons:**
    *   *Primary:* Gradient fill (`primary` to `primary_container`) with `on_primary` text. `xl` (1.5rem) corner radius.
    *   *Secondary:* `secondary_container` fill with `on_secondary_container` text. No border.
*   **ISL Video Cards:** 
    *   Forbid divider lines. Use `surface_container_highest` for the video wrapper and `3` (1rem) spacing to separate the video from the text gloss below.
*   **Status Indicators (Camera/Mic):**
    *   Use `secondary_fixed` for "Active" states (a soft teal glow) and `error_container` for "Off" states. These should be housed in glassmorphic floating "pills."
*   **Input Fields:** 
    *   Use `surface_container_high` for the field background. On focus, transition the background to `surface_container_lowest` and add a 1px "Ghost Border."
*   **Chips:** 
    *   Use `full` roundedness (pill shape). Filter chips should use `tertiary_fixed` to distinguish them from primary actions.

## 6. Do’s and Don’ts

### Do:
*   **Embrace Negative Space:** Use the `12` (4rem) and `16` (5.5rem) spacing tokens liberally between major sections to let the sign language content "breathe."
*   **Use Tonal Shifts:** Always use background color changes to define card boundaries before reaching for a shadow.
*   **Prioritize the Video Feed:** Ensure the video feed (the "human" element) is always the highest-contrast element on the screen.

### Don't:
*   **No 100% Black:** Never use `#000000` for text; use `on_surface` (`#191c1e`) to maintain a premium, soft-UI feel.
*   **No Sharp Corners:** Avoid the `none` or `sm` roundedness tokens for main containers. Stick to `lg` (1rem) for cards to maintain the "approachable" brand promise.
*   **No Dividers:** Avoid horizontal rules (`<hr>`). Use the `6` (2rem) spacing token to create a "visual break" through silence rather than a line.
*   **No Flat Buttons:** Avoid purely flat, single-color primary buttons. Always add a subtle tonal gradient to imply a "pressable" 3D surface.