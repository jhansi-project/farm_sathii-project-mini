import React, { useState, useEffect } from 'react';
import { Navbar } from './Navbar';
import { BottomNav } from './BottomNav';
import { AppNavTab } from '../../features/dashboard/DashboardView';
import { useTranslation } from '../../i18n/useTranslation';

interface DashboardLayoutProps {
  children: React.ReactNode;
  activeTab: AppNavTab;
  onChangeTab: (tab: AppNavTab) => void;
  onOpenAuth: () => void;
  onOpenProfile: () => void;
  hideNav?: boolean;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  activeTab,
  onChangeTab,
  onOpenAuth,
  onOpenProfile,
  hideNav = false,
}) => {
  const { t } = useTranslation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Close sidebar on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsSidebarOpen(false);
      }
    };
    if (isSidebarOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isSidebarOpen]);

  const navItems: Array<{ id: AppNavTab; label: string; icon: string }> = [
    { id: 'home', label: t.nav.home, icon: 'home' },
    { id: 'ask', label: t.nav.ask, icon: 'forum' },
    { id: 'crops', label: t.nav.cropRecommendation, icon: 'psychology' },
    { id: 'diagnosis', label: t.nav.diagnosis, icon: 'photo_camera' },
    { id: 'my-crops', label: t.nav.myCrops, icon: 'agriculture' },
    { id: 'history', label: t.nav.history, icon: 'history' },
  ];

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'var(--color-background)',
        overflowX: 'hidden',
        position: 'relative',
      }}
    >
      {/* 1. Header with Brand & Navigation */}
      <Navbar
        onOpenAuth={onOpenAuth}
        onOpenProfile={onOpenProfile}
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        isSidebarOpen={isSidebarOpen}
        activeTab={activeTab}
        onChangeTab={onChangeTab}
      />

      {/* Agricultural Atmospheric Background Layer (IMAGE 2: Wide green rice field) */}
      <div
        aria-hidden="true"
        style={{
          position: 'fixed',
          top: 'var(--header-height, 64px)',
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: 'url(/assets/rice_field_bg.png)',
          backgroundPosition: 'center top',
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
          opacity: 0.75,
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />

      {/* Subtle FarmSathi Tint Overlay (Bone #E5D7C4 at 25% strength) */}
      <div
        aria-hidden="true"
        style={{
          position: 'fixed',
          top: 'var(--header-height, 64px)',
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(229, 215, 196, 0.25)',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />

      {/* 2. Off-canvas Backdrop Overlay */}
      {!hideNav && (
        <div
          onClick={() => setIsSidebarOpen(false)}
          aria-hidden="true"
          style={{
            position: 'fixed',
            top: 'var(--header-height)',
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(53, 64, 36, 0.55)',
            backdropFilter: 'blur(3px)',
            WebkitBackdropFilter: 'blur(3px)',
            zIndex: 40,
            opacity: isSidebarOpen ? 1 : 0,
            visibility: isSidebarOpen ? 'visible' : 'hidden',
            pointerEvents: isSidebarOpen ? 'auto' : 'none',
            transition: 'opacity 0.22s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.22s ease',
          }}
        />
      )}

      {/* 3. Off-canvas Navigation Drawer */}
      {!hideNav && (
        <aside
          aria-label="Application Navigation"
          aria-hidden={!isSidebarOpen}
          style={{
            position: 'fixed',
            left: 0,
            top: 'var(--header-height)',
            width: '280px',
            maxWidth: '85vw',
            height: 'calc(100vh - var(--header-height))',
            backgroundColor: 'var(--color-header-bg, #2f3e20)',
            borderRight: '1px solid var(--color-header-border, #2f3e20)',
            boxShadow: isSidebarOpen ? 'var(--shadow-lg)' : 'none',
            padding: '1.25rem 0.85rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
            overflowY: 'auto',
            zIndex: 45,
            transform: isSidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
            visibility: isSidebarOpen ? 'visible' : 'hidden',
            pointerEvents: isSidebarOpen ? 'auto' : 'none',
            transition:
              'transform 0.22s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.22s ease, box-shadow 0.22s ease',
          }}
        >
          {/* Drawer Header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0 0.5rem 0.75rem 0.5rem',
              marginBottom: '0.5rem',
              borderBottom: '1px solid var(--color-border, #CFBB99)',
            }}
          >
            <img
              src="/assets/farmsathi_logo.png"
              alt="FarmSathi"
              style={{
                height: '32px',
                width: 'auto',
                objectFit: 'contain',
                display: 'block',
              }}
            />
            <button
              type="button"
              onClick={() => setIsSidebarOpen(false)}
              aria-label="Close navigation menu"
              title="Close navigation menu"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-full)',
                color: 'var(--color-header-text, #E5D7C4)',
                cursor: 'pointer',
                transition: 'background-color var(--transition-fast)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(136, 144, 99, 0.25)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                close
              </span>
            </button>
          </div>

          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  onChangeTab(item.id);
                  setIsSidebarOpen(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.85rem',
                  padding: '0.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: isActive ? 'var(--color-active, #889063)' : 'transparent',
                  color: isActive ? 'var(--color-text-inverse, #E5D7C4)' : 'var(--color-header-text, #E5D7C4)',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: 'var(--font-size-sm)',
                  transition: 'all var(--transition-fast)',
                  textAlign: 'left',
                  width: '100%',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.backgroundColor = 'rgba(136, 144, 99, 0.25)';
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <span
                  className="material-symbols-outlined"
                  style={{
                    fontSize: '22px',
                    color: 'inherit',
                    fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0",
                  }}
                >
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </aside>
      )}

      {/* 4. Main Content Area */}
      <main
        style={{
          flex: 1,
          width: '100%',
          minHeight: 'calc(100vh - var(--header-height))',
          position: 'relative',
          zIndex: 1,
          overflowX: 'hidden',
        }}
      >
        {children}
      </main>

      {/* 5. Mobile Bottom Navigation */}
      {!hideNav && <BottomNav activeTab={activeTab} onChangeTab={onChangeTab} />}
    </div>
  );
};
