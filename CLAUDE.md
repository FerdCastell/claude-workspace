# Claude Code — Project Instructions

## About this workspace
This directory is used for design, video, storyboards, internet research, and analysis work. Primary scripting language is Python.

## Code style
- Match the conventions already present in the project (indentation, naming, formatting)
- Do not reformat or clean up code outside the scope of the requested change
- No unnecessary comments or docstrings on unchanged code

## Commits
- **Never auto-commit.** Always ask before running `git commit`
- Stage only the specific files related to the change — never `git add -A` or `git add .`

## Testing
- Always run tests after making code changes
- Report test results before considering a task complete

## Communication style
- Keep responses short and direct — no padding, no unnecessary preamble
- No emojis
- Use markdown only where it adds clarity

## Python
- Prefer standard library where possible; flag when a third-party package is needed
- Use virtual environments; do not install packages globally without asking

---

# Remotion Video Skill

This workspace supports Remotion-based video production using React.

Full remotion docs: https://www.remotion.dev/docs/

## Project structure

Root file is `src/Root.tsx`:

```typescript
import {Composition} from 'remotion';
import {MyComp} from './MyComp';

export const Root: React.FC = () => {
	return (
		<>
			<Composition
				id="MyComp"
				component={MyComp}
				durationInFrames={120}
				width={1920}
				height={1080}
				fps={30}
				defaultProps={{}}
			/>
		</>
	);
};
```

A `<Composition>` defines a renderable video. Default: 30fps, 1920x1080, id="MyComp".

Inside components, use `useCurrentFrame()` to get the current frame (starts at 0).

## Component Rules

- Video: `<OffthreadVideo>`
- Static image: `<Img>`
- Animated GIF: install `@remotion/gif`, use `<Gif>`
- Audio: `<Audio>`
- Assets: local via `staticFile()` from `public/`, or remote URLs

Key animation helpers:
- `interpolate(frame, inputRange, outputRange, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})`
- `spring({fps, frame, config: {damping: 200}})`
- `random('seed')` — deterministic randomness (never `Math.random()`)
- `useVideoConfig()` — access fps, durationInFrames, height, width

Layout/timing:
- `AbsoluteFill` — layer elements
- `Sequence` — place at specific frame (`from`, `durationInFrames`)
- `Series` / `Series.Sequence` — sequential elements
- `TransitionSeries` from `@remotion/transitions` — transitions between sequences

## Remotion vs Normal React

No `useState` for interactivity, no `onClick`/`onHover`, no `useEffect` for side effects. All animation is driven by `useCurrentFrame()`. Components are deterministic and frame-by-frame.
