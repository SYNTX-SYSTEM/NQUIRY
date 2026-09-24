/**
 * F02 page chrome: brand, breadcrumb trail (orientation, not navigation
 * state), logout. Domain content lives in <main id="main">. Mocked suites
 * scope their "no action element in main" proofs to <main>, so logout stays
 * in the header.
 */
import Link from "next/link";
import { LogoutButton } from "../LogoutButton";

export type Crumb = { readonly label: string; readonly href?: string };

export function AppShell({ crumbs, children }: { readonly crumbs: readonly Crumb[]; readonly children: React.ReactNode }) {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="shell-header">
        <Link className="brand" href="/workspaces">
          nquiry
        </Link>
        <nav aria-label="Breadcrumb" className="breadcrumbs">
          <ol>
            {crumbs.map((crumb, index) => (
              <li key={`${crumb.label}-${index}`}>
                {crumb.href && index < crumbs.length - 1 ? (
                  <Link href={crumb.href}>{crumb.label}</Link>
                ) : (
                  <span aria-current={index === crumbs.length - 1 ? "page" : undefined}>{crumb.label}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>
        <LogoutButton />
      </header>
      <main id="main" className="shell-main">
        {children}
      </main>
    </>
  );
}
