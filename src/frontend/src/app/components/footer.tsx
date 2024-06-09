import { FC } from "react";

export const Footer: FC = () => {
  return (
    <div className="flex flex-col items-center gap-1 text-center text-xs text-zinc-700">
      <div className="text-zinc-400">私有数据，仅供测试，请勿传播。</div>
      <div className="mt-2 flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-zinc-400">
        <a className="hover:text-zinc-950" href="https://lepton.ai/">
          UI 由 Lepton Search 驱动
        </a>
      </div>
    </div>
  );
};
