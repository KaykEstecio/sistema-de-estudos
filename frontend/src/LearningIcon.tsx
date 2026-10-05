type IconName = 'home' | 'code' | 'profile' | 'target' | 'growth' | 'review'

const paths: Record<IconName, string> = {
  home: 'M3 10 12 3l9 7M5 9v11h5v-6h4v6h5V9',
  code: 'm8 6-5 6 5 6m8-12 5 6-5 6m-3-14-2 16',
  profile: 'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0ZM4 21v-2a8 8 0 0 1 16 0v2',
  target: 'M20 12a8 8 0 1 1-8-8m4 8a4 4 0 1 1-4-4m0 4 9-9m-5 0h5v5',
  growth: 'M5 20v-5m7 5v-9m7 9V6M3 10l6-5 5 2 6-5',
  review: 'M8 4H5v17h14V4h-3M8 2h8v5H8Zm0 12 3 3 5-6',
}

/** Decorative icons: the adjacent text supplies the accessible label. */
export default function LearningIcon({ name }: { name: IconName }) {
  return <svg className={`learning-icon icon-${name}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><path d={paths[name]} /></svg>
}
