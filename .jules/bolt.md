## 2026-06-25 - Avoid Python nested loops for pixel modification in Pygame
**Learning:** Editing pixels element-by-element using Python's nested `for` loops and `pygame.Surface.get_at`/`set_at` is painfully slow and a major performance bottleneck (taking multiple seconds on large surfaces). Pygame offers native C-accelerated blending and filling.
**Action:** When applying a uniform color transformation or blend over a Pygame surface, always use `surface.fill(color, special_flags=pygame.BLEND_*)` (like `BLEND_RGBA_ADD`) or `surface.blit` instead of iterating over every single pixel manually.
