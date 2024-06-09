import { FC, ReactNode } from "react";

export const Wrapper: FC<{
  title: ReactNode;
  content: ReactNode;
}> = ({ title, content }) => {
  return (
    <div className="flex w-full flex-col gap-4">
      <div className="flex gap-2 text-blue-500">{title}</div>
      {content}
    </div>
  );
};
