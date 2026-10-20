# Axon UI

`axon-ui` is a small reactive UI library built on top of `pygame` and `pygame_gui`. It provides the scaffolding for a retained-mode desktop app - a window, a render loop, a stack of screens, and a tree of reusable components. It is driven by a single reactive primitive, the `Atom`, that lets UI update itself in response to state changes instead of being redrawn or polled by hand.

The library is intentionally minimal. It does not ship widgets; see the `axon-ui-kit` package for pre-built components.

## Building blocks

- `Atom`: a minimal observable value (`Atom.value`). Clients subscribe, and any changes are propagated back to every subscriber.
- `Component`: a reusable, self-contained piece of UI that owns a group of `pygame_gui` elements and, optionally, nested child components. Components subscribe to `Atom`s via `Component.bind` and re-render themselves in the callback.
- `Screen`: one full-window "page." It pairs a `pygame_gui.UIManager` with a single root `Component` and can request navigation to another screen.
- `App`: the top-level object. It owns the window and render loop and drives the active screen every frame.
- `axon.router.Router`: the internal machine used by `App` to forward the render loop to the current screen and drive navigation.

## Quick start

...

## Design philosophy

...
