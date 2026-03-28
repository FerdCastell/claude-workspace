import React from 'react';
import {Composition} from 'remotion';
import {ProductLaunch} from './ProductLaunch';

export const Root: React.FC = () => {
	return (
		<>
			<Composition
				id="MyComp"
				component={ProductLaunch}
				durationInFrames={210}
				width={1920}
				height={1080}
				fps={30}
				defaultProps={{
					productName: 'Horizon',
					tagline: 'The future, rendered frame by frame.',
					accentColor: '#6C63FF',
				}}
			/>
		</>
	);
};
