import { SignUp } from "@clerk/nextjs";

export default function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--muted)]">
      <div className="text-center">
        <h1 className="mb-8 text-3xl font-bold text-brand-600">NeuraProp AI</h1>
        <SignUp afterSignUpUrl="/overview" />
      </div>
    </div>
  );
}
