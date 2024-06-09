"use client";
import { Footer } from "@/app/components/footer";
import { Logo } from "@/app/components/logo";
import { Search } from "@/app/components/search";

export default function Home() {
  return (
    <div
      id="screen"
      className="absolute inset-0 items-center justify-center overflow-auto bg-grid"
    >
      <div
        id="content"
        className="relative mx-auto mt-10 flex min-w-[960px] max-w-[1600px] flex-col items-center gap-8"
      >
        <Logo />
        <Search />
        <Footer />
      </div>
    </div>
  );
}
