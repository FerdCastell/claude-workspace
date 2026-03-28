import React from 'react';
import {
	AbsoluteFill,
	interpolate,
	spring,
	useCurrentFrame,
	useVideoConfig,
	Sequence,
} from 'remotion';

type Props = {
	productName: string;
	tagline: string;
	accentColor: string;
};

const Background: React.FC<{accentColor: string}> = ({accentColor}) => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();

	const hue = interpolate(frame, [0, durationInFrames], [220, 280]);

	return (
		<AbsoluteFill
			style={{
				background: `radial-gradient(ellipse at 50% 50%, hsl(${hue}, 60%, 12%) 0%, #050508 70%)`,
			}}
		/>
	);
};

const GridLines: React.FC = () => {
	const frame = useCurrentFrame();
	const opacity = interpolate(frame, [0, 40], [0, 0.12], {
		extrapolateRight: 'clamp',
	});

	const lines = Array.from({length: 12});
	return (
		<AbsoluteFill style={{opacity}}>
			{lines.map((_, i) => (
				<div
					key={i}
					style={{
						position: 'absolute',
						left: `${(i / 12) * 100}%`,
						top: 0,
						width: 1,
						height: '100%',
						background: 'rgba(255,255,255,0.4)',
					}}
				/>
			))}
			{lines.map((_, i) => (
				<div
					key={`h${i}`}
					style={{
						position: 'absolute',
						top: `${(i / 12) * 100}%`,
						left: 0,
						height: 1,
						width: '100%',
						background: 'rgba(255,255,255,0.4)',
					}}
				/>
			))}
		</AbsoluteFill>
	);
};

const LogoMark: React.FC<{accentColor: string}> = ({accentColor}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const scale = spring({fps, frame, config: {damping: 14, stiffness: 80}});
	const opacity = interpolate(frame, [0, 15], [0, 1], {
		extrapolateRight: 'clamp',
	});

	const rotate = interpolate(frame, [0, 60], [0, 360], {
		extrapolateRight: 'clamp',
	});

	return (
		<div
			style={{
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				transform: `scale(${scale})`,
				opacity,
			}}
		>
			<svg
				width="120"
				height="120"
				viewBox="0 0 120 120"
				style={{transform: `rotate(${rotate}deg)`}}
			>
				<defs>
					<linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
						<stop offset="0%" stopColor={accentColor} stopOpacity="1" />
						<stop offset="100%" stopColor="#ff6b6b" stopOpacity="1" />
					</linearGradient>
				</defs>
				<polygon
					points="60,10 110,85 10,85"
					fill="none"
					stroke="url(#logoGrad)"
					strokeWidth="6"
					strokeLinejoin="round"
				/>
				<polygon
					points="60,35 87,75 33,75"
					fill="url(#logoGrad)"
					opacity="0.6"
				/>
			</svg>
		</div>
	);
};

const Title: React.FC<{productName: string; accentColor: string}> = ({
	productName,
	accentColor,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const y = spring({fps, frame, config: {damping: 18, stiffness: 100}});
	const translateY = interpolate(y, [0, 1], [60, 0]);
	const opacity = interpolate(frame, [0, 20], [0, 1], {
		extrapolateRight: 'clamp',
	});

	return (
		<div
			style={{
				transform: `translateY(${translateY}px)`,
				opacity,
				textAlign: 'center',
			}}
		>
			<div
				style={{
					fontSize: 160,
					fontWeight: 900,
					fontFamily: 'system-ui, -apple-system, sans-serif',
					letterSpacing: '-6px',
					color: 'white',
					lineHeight: 1,
					textShadow: `0 0 80px ${accentColor}88`,
				}}
			>
				{productName}
			</div>
		</div>
	);
};

const Tagline: React.FC<{tagline: string}> = ({tagline}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const progress = spring({fps, frame, config: {damping: 20, stiffness: 80}});
	const translateY = interpolate(progress, [0, 1], [30, 0]);
	const opacity = interpolate(frame, [0, 25], [0, 1], {
		extrapolateRight: 'clamp',
	});

	return (
		<div
			style={{
				transform: `translateY(${translateY}px)`,
				opacity,
				textAlign: 'center',
				marginTop: 32,
			}}
		>
			<div
				style={{
					fontSize: 36,
					fontFamily: 'system-ui, -apple-system, sans-serif',
					fontWeight: 300,
					letterSpacing: '4px',
					color: 'rgba(255,255,255,0.65)',
					textTransform: 'uppercase',
				}}
			>
				{tagline}
			</div>
		</div>
	);
};

const AccentLine: React.FC<{accentColor: string}> = ({accentColor}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const progress = spring({fps, frame, config: {damping: 20}});
	const width = interpolate(progress, [0, 1], [0, 320]);

	return (
		<div
			style={{
				height: 3,
				width,
				background: `linear-gradient(90deg, ${accentColor}, #ff6b6b)`,
				borderRadius: 2,
				marginTop: 28,
				boxShadow: `0 0 20px ${accentColor}`,
			}}
		/>
	);
};

const OutroFade: React.FC = () => {
	const frame = useCurrentFrame();
	const opacity = interpolate(frame, [0, 30], [0, 1], {
		extrapolateRight: 'clamp',
	});

	return (
		<AbsoluteFill
			style={{background: 'black', opacity}}
		/>
	);
};

export const ProductLaunch: React.FC<Props> = ({
	productName,
	tagline,
	accentColor,
}) => {
	const {durationInFrames} = useVideoConfig();
	const outroStart = durationInFrames - 30;

	return (
		<AbsoluteFill style={{fontFamily: 'system-ui, sans-serif'}}>
			<Background accentColor={accentColor} />
			<GridLines />

			{/* Logo — enters at frame 0 */}
			<AbsoluteFill
				style={{
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
					flexDirection: 'column',
					marginBottom: 260,
				}}
			>
				<LogoMark accentColor={accentColor} />
			</AbsoluteFill>

			{/* Title — enters at frame 30 */}
			<Sequence from={30}>
				<AbsoluteFill
					style={{
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						flexDirection: 'column',
					}}
				>
					<Title productName={productName} accentColor={accentColor} />
					<AccentLine accentColor={accentColor} />
				</AbsoluteFill>
			</Sequence>

			{/* Tagline — enters at frame 60 */}
			<Sequence from={60}>
				<AbsoluteFill
					style={{
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						flexDirection: 'column',
						marginTop: 260,
					}}
				>
					<Tagline tagline={tagline} />
				</AbsoluteFill>
			</Sequence>

			{/* Outro fade to black */}
			<Sequence from={outroStart}>
				<OutroFade />
			</Sequence>
		</AbsoluteFill>
	);
};
