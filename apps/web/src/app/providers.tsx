import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { PropsWithChildren } from "react";
import { AuthProvider } from "../state/auth/AuthContext";
import { ToastProvider } from "../components/ToastProvider";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 5 * 60 * 1000, refetchOnWindowFocus: false },
    mutations: { retry: false },
  },
});

export function AppProviders({ children }: PropsWithChildren): React.JSX.Element {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>{children}</ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

