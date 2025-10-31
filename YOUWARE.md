# QIC LifePlus - Development Guide

A modern wellness and rewards platform prototype for Qatar Insurance Company (QIC) built with React, TypeScript, and Vite.

## Quick Setup

```bash
npm install      # Install dependencies
npm run dev      # Start development server (http://localhost:5173)
npm run build    # Build for production
npm run preview  # Preview production build
```

## Project Architecture

### Core Structure
```
src/
├── pages/Dashboard.tsx          # Main dashboard page with state management
├── components/Dashboard/        # Reusable dashboard components
│   ├── UserCard.tsx            # User profile and stats
│   ├── GoalCard.tsx            # Individual goal with progress
│   └── TaskItem.tsx            # Task list item with completion
├── types/index.ts              # TypeScript interfaces (User, Goal, Task)
├── App.tsx                     # Root component with gradient background
├── App.css                     # Global animations
└── main.tsx                    # React entry point
```

### State Management
- **Location**: `src/pages/Dashboard.tsx` (lines 1-100)
- **Pattern**: React `useState` hooks for local component state
- **Data Structure**: In-memory sample data; easily migrates to localStorage or backend
- **Interfaces**: All types defined in `src/types/index.ts` for type safety

### Component Hierarchy
```
App (gradient background)
└── Dashboard (state container)
    ├── UserCard (user metrics)
    ├── GoalCard[] (monthly goals with progress)
    └── TaskItem[] (daily/weekly tasks)
```

## Development Workflow

### Common Tasks

**Adding a new goal:**
1. Edit `initialGoals` in `src/pages/Dashboard.tsx` (around line 40)
2. Follow the Goal interface structure from `src/types/index.ts`
3. Choose a color: `'blue' | 'green' | 'purple' | 'pink' | 'orange'`
4. Changes reflect immediately with HMR

**Adding a new task:**
1. Edit `initialTasks` in `src/pages/Dashboard.tsx` (around line 70)
2. Set point values and category
3. No rebuild needed; Vite's HMR updates instantly

**Styling changes:**
- **Tailwind CSS**: Use utility classes in JSX
- **Custom CSS**: Add to `src/App.css` for global animations
- **Component styles**: Use Tailwind classes directly in component JSX
- **Color palette**: Extend in `tailwind.config.js` (custom brand colors defined)

**Animation tuning:**
- Global animations in `src/App.css`
- Tailwind `transition` classes for smooth interactions
- GSAP/Framer Motion libraries available but not currently used

## Tech Stack

| Purpose | Tool | Version |
|---------|------|---------|
| Framework | React | 18.3.1 |
| Language | TypeScript | 5.8.3 |
| Build Tool | Vite | 7.0.0 |
| CSS Framework | Tailwind | 3.4.17 |
| Icons | Lucide React | Latest |
| State (Future) | Zustand | 4.4.7 |
| Routing (Future) | React Router | 6.30.1 |

## Key Features

**Implemented:**
- ✅ Interactive goal tracking with progress bars
- ✅ Daily/weekly task management with point rewards
- ✅ User metrics dashboard (streak, level, total points, wellness score)
- ✅ Smooth animations and hover effects
- ✅ Fully responsive design (mobile, tablet, desktop)
- ✅ TypeScript type safety across all components

**Architecture ready for:**
- LocalStorage persistence (data structure supports easy integration)
- Backend API integration (state easily moves to server)
- Rewards page (component pattern established)
- User authentication (User interface prepared)

## Configuration Files

### `vite.config.ts`
- Fast HMR development server
- Production minification enabled
- Asset optimization configured

### `tailwind.config.js`
- Extended color palette with brand colors
- Custom `inter` font family
- Shadow utilities for depth effects
- Preset animations defined

### `tsconfig.json`
- Strict mode enabled for type safety
- JSX support configured
- Path aliases available

### `package.json`
- Development dependencies: React, TypeScript, Vite
- Build scripts: `dev`, `build`, `preview`
- No backend dependencies (frontend-only prototype)

## Performance Notes

- **Bundle Size**: ~51 kB gzipped (checked after `npm run build`)
- **Development**: Vite provides sub-second HMR updates
- **Production**: CSS and JS minified; no unused code shipped
- **Rendering**: React memo and useMemo available for optimization (not currently needed)

## Customization Guide

### Change User Data
Edit `src/pages/Dashboard.tsx` line ~35:
```typescript
const initialUser: User = {
  name: 'Ahmed',
  level: 5,
  currentStreak: 12,
  totalPoints: 2840,
  wellnessScore: 78,
};
```

### Change Color Scheme
Two locations:
1. **Tailwind config**: `tailwind.config.js` (global brand colors)
2. **Component map**: `src/components/Dashboard/GoalCard.tsx` (colorMap object)

### Extend Sample Data
All sample data is hardcoded in `src/pages/Dashboard.tsx`. Structure:
- `initialUser`: Single user object
- `initialGoals`: Array of Goal objects
- `initialTasks`: Array of Task objects

No migrations or seeders needed; directly modify arrays.

## Building and Deployment

**Production build:**
```bash
npm run build
# Output in dist/ folder (ready to deploy)
```

**Deployment options:**
- **Static hosting**: Upload `dist/` folder to any static host (Vercel, Netlify, etc.)
- **Local preview**: `npm run preview` or `npx serve -s dist`
- **Docker**: Create Dockerfile in project root if containerization needed

## Debugging

**Check console errors:**
- Open browser DevTools (F12)
- Check Console tab for TypeScript or runtime errors
- Watch Network tab for failed asset loads

**TypeScript compilation check:**
```bash
npx tsc --noEmit
```

**Clear cache and rebuild:**
```bash
rm -rf node_modules dist .vite
npm install
npm run build
```

## File-Level Reference

| File | Purpose | Key Lines |
|------|---------|-----------|
| `src/pages/Dashboard.tsx` | Main state & layout | 1-200 |
| `src/types/index.ts` | Data interfaces | 1-40 |
| `src/components/Dashboard/GoalCard.tsx` | Goal rendering | colorMap at line 5 |
| `src/App.css` | Global animations | All keyframes |
| `tailwind.config.js` | Style configuration | extend section |
| `vite.config.ts` | Build config | React plugin |

## Future Enhancements

Listed in priority order for next phases:

1. **LocalStorage Persistence** - Save user progress across sessions
2. **Rewards Page** - Show QIC insurance discounts and perks
3. **Profile Page** - User customization and settings
4. **Backend Integration** - Sync with QIC systems (requires Youware Backend)
5. **Leaderboard** - Compete with other users
6. **Push Notifications** - Alert users for achievements
7. **Social Sharing** - Share progress with friends

## Troubleshooting

**Port 5173 in use:**
```bash
npm run dev -- --port 3000
```

**Module not found errors:**
```bash
rm -rf node_modules
npm install
```

**TypeScript strict mode errors:**
Check that all variables have explicit types. Run `npx tsc --noEmit` to see all issues.

**Build fails:**
- Check Node version (must be 18+): `node --version`
- Increase memory if needed: `NODE_OPTIONS="--max-old-space-size=4096" npm run build`

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Setup Scripts

Two convenience scripts included:

**SETUP.sh** - Interactive setup for Linux
```bash
chmod +x SETUP.sh
./SETUP.sh
# Checks prerequisites, installs deps, builds project
```

**INSTALL.md** - Comprehensive setup documentation with troubleshooting

---

**Last updated:** Oct 31, 2025 | **Project Type:** React + TypeScript | **Status:** Production-ready prototype
