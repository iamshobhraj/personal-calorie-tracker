import { RouterProvider } from "react-router-dom";
import { AppProviders } from "./providers";
import { router } from "./router";
import { ErrorBoundary } from "../components/ErrorBoundary";

export function App(): React.JSX.Element {
  return (
    <ErrorBoundary><AppProviders><RouterProvider router={router} /></AppProviders></ErrorBoundary>
  );
}
