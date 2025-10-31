# QIC LifePlus - Installation & Setup Guide (Linux)

This guide will help you set up and run the QIC LifePlus wellness dashboard on your Linux system.

## Prerequisites

Ensure you have the following installed on your system:

- **Node.js** (v18.0.0 or higher) - [Download](https://nodejs.org/)
- **npm** (v9.0.0 or higher) - Comes with Node.js
- **Git** (optional, for version control)
- **Unzip utility** (to extract the zip file)

### Check Your Installation

```bash
node --version    # Should be v18+
npm --version     # Should be v9+
```

## Setup Instructions

### Step 1: Extract the Project

```bash
# Navigate to your desired directory
cd ~/projects  # or any directory you prefer

# Extract the zip file
unzip qic-lifeplus.zip -d qic-lifeplus

# Navigate into the project directory
cd qic-lifeplus
```

### Step 2: Install Dependencies

```bash
# Install all required packages
npm install

# This will install:
# - React 18.3.1
# - TypeScript 5.8.3
# - Vite 7.0.0
# - Tailwind CSS 3.4.17
# - And other dependencies
```

**Expected output:** You should see a message like:
```
added 500+ packages in X seconds
```

### Step 3: Run the Development Server

```bash
# Start the development server
npm run dev

# Output:
# ➜  Local:   http://localhost:5173/
# ➜  Press q to quit
```

Open your browser and navigate to: **http://localhost:5173/**

You should see the QIC LifePlus dashboard with:
- User welcome card with streak counter
- Monthly goals with progress bars
- Daily tasks section
- Interactive completion tracking

### Step 4: Build for Production (Optional)

```bash
# Create an optimized production build
npm run build

# Output will show build status and file sizes
# Typical output: dist/assets/index-*.js (~ 51 kB gzipped)
```

The production build is saved in the `dist/` folder.

### Step 5: Preview Production Build (Optional)

```bash
# Install serve globally (one-time setup)
npm install -g serve

# Preview the production build locally
npm run preview
# or
serve -s dist

# Navigate to: http://localhost:3000/
```

## Project Structure

```
qic-lifeplus/
├── src/                      # Source code
│   ├── components/           # React components
│   │   └── Dashboard/        # Dashboard sub-components
│   ├── pages/                # Page components
│   ├── types/                # TypeScript interfaces
│   ├── App.tsx               # Main app component
│   └── main.tsx              # React entry point
├── dist/                     # Production build (after npm run build)
├── public/                   # Static assets
├── package.json              # Project dependencies
├── vite.config.ts            # Vite build configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
├── YOUWARE.md                # Development guidelines
└── INSTALL.md                # This file
```

## Available Commands

### Development

```bash
npm run dev       # Start development server (http://localhost:5173)
```

### Production

```bash
npm run build     # Build for production
npm run preview   # Preview production build locally
```

### Other Useful Commands

```bash
# Check TypeScript compilation
npx tsc --noEmit

# List available scripts
npm run
```

## Troubleshooting

### Issue: "npm: command not found"

**Solution:** Node.js and npm are not installed.
```bash
# On Ubuntu/Debian:
sudo apt update && sudo apt install nodejs npm

# On Fedora:
sudo dnf install nodejs npm

# On Arch:
sudo pacman -S nodejs npm

# Verify installation:
node --version
npm --version
```

### Issue: "Port 5173 is already in use"

**Solution:** Kill the process using that port or use a different port.
```bash
# Find the process using port 5173
lsof -i :5173

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port
npm run dev -- --port 3000
```

### Issue: "node-sass build errors" or "dependency issues"

**Solution:** Clear npm cache and reinstall.
```bash
# Remove node_modules and lock file
rm -rf node_modules package-lock.json

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
npm install
```

### Issue: TypeScript errors on start

**Solution:** Ensure your Node.js version is compatible.
```bash
# Check Node version (should be 18.0.0 or higher)
node --version

# If too old, update Node.js using nvm (Node Version Manager):
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### Issue: "Cannot find module" errors

**Solution:** Reinstall dependencies and clear cache.
```bash
npm install --legacy-peer-deps
npm run build
```

### Issue: Build fails with memory error

**Solution:** Increase Node's memory allocation.
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

## Environment Variables

Create a `.env.local` file in the project root if needed:

```bash
# .env.local
VITE_API_URL=http://localhost:3000
VITE_ENV=development
```

(Not required for the basic prototype)

## Performance Tips

### Development
- Use `npm run dev` for fast hot module reloading
- Keep browser DevTools open to monitor performance
- Check console for any warnings or errors

### Production
- Always run `npm run build` before deployment
- Use a static server to serve the `dist/` folder
- Optimize images and assets in `public/` folder
- Enable gzip compression on your web server

## Project Features

The QIC LifePlus dashboard includes:

✅ **Interactive Goals** - Track 5 wellness goals with progress bars
✅ **Daily Tasks** - Complete tasks and earn points
✅ **Gamification** - Levels, streaks, and achievement tracking
✅ **Responsive Design** - Works on desktop, tablet, and mobile
✅ **Modern UI** - Beautiful gradient backgrounds and smooth animations
✅ **Type-Safe** - Full TypeScript support

## Next Steps

### Customize the App

Edit `src/pages/Dashboard.tsx` to modify:
- User data (name, level, points)
- Goals and their targets
- Tasks and point values
- Colors and styling

### Add Features

Potential enhancements:
- Rewards page showing QIC insurance discounts
- User profile section
- LocalStorage persistence
- Backend integration
- Leaderboard system

See `YOUWARE.md` for architectural details.

## Getting Help

- **TypeScript Errors**: Check `tsconfig.json` and ensure IDE supports TypeScript
- **Build Issues**: Clear `node_modules` and reinstall with `npm install`
- **Port Issues**: Change the port using `npm run dev -- --port <PORT>`
- **Documentation**: See `README.md` for project overview

## Uninstalling

To remove the project:

```bash
# Remove the entire directory
cd ~/projects
rm -rf qic-lifeplus
```

To uninstall globally installed packages:

```bash
npm uninstall -g serve  # If you installed serve
```

---

**Happy coding! 🚀** For more details, see `README.md` and `YOUWARE.md`.
