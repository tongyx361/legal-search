import { Wrapper } from "@/app/components/wrapper";
import LawDocument from "@/app/interfaces/lawdocument";
import { BookText, ChevronDown, ChevronUp } from "lucide-react";
import { FC, useEffect, useRef, useState } from "react";

// LawDoc component to display a single law document
const LawDoc: FC<{ document: LawDocument; index: number }> = ({
  document,
  index,
}) => {
  const { title, full, laws, judges, keywords, highlights } = document;

  const [expanded, setExpanded] = useState(false);

  const CustomList: FC<{
    prompt: string;
    items: string[];
    itemColor: string;
  }> = ({ prompt, items, itemColor }) => {
    return (
      <div className={`my-1 flex flex-wrap items-center text-xs`}>
        {prompt}
        {items.map((item: string, i: number) => (
          <span
            key={i}
            className={`mx-1 my-1 whitespace-nowrap rounded-md ${itemColor} px-1 py-1 text-xs`}
          >
            {item}
          </span>
        ))}
      </div>
    );
  };

  const highlightKeywords = (text: string, highlights: string[]) => {
    const highlightColorClasses = [
      "bg-yellow-200",
      "bg-blue-200",
      "bg-green-200",
      "bg-pink-200",
      "bg-purple-200",
      "bg-red-200",
      "bg-indigo-200",
      "bg-gray-200",
      "bg-yellow-300",
      "bg-blue-300",
      "bg-green-300",
      "bg-pink-300",
      "bg-purple-300",
      "bg-red-300",
      "bg-indigo-300",
      "bg-gray-300",
    ];

    let highlightedText = text;

    highlights.forEach((keyword, index) => {
      const regex = new RegExp(keyword, "gi");
      highlightedText = highlightedText.replace(regex, (match) => {
        const colorClass =
          highlightColorClasses[index % highlightColorClasses.length];
        return `<span class="${colorClass}">${match}</span>`;
      });
    });

    return { __html: highlightedText };
  };

  return (
    <div className="mb-4 flex flex-col items-center rounded-md border border-gray-300 p-4">
      <div
        id="doc-header"
        className="items-left justify-left m-1 flex w-full flex-col"
      >
        <h3 className="mb-2 text-lg font-semibold">{title}</h3>
        <CustomList
          prompt="法官："
          items={judges}
          itemColor="bg-blue-200 text-blue-800"
        />
        <CustomList
          prompt="法条："
          items={laws}
          itemColor="bg-teal-200 text-teal-800"
        />
        <CustomList
          prompt="关键词："
          items={keywords}
          itemColor="bg-gray-200 text-gray-800"
        />
      </div>
      {expanded && (
        <>
          {" "}
          <button
            className="mt-2 flex items-center text-blue-500"
            onClick={() => setExpanded(!expanded)} // 将展开状态取反
          >
            {expanded ? (
              <>
                收起全文
                <ChevronUp />
              </>
            ) : (
              <>
                展开全文
                <ChevronDown />
              </>
            )}
          </button>{" "}
          <div
            className="m-2 w-full rounded-md border bg-white p-2 text-sm leading-6"
            dangerouslySetInnerHTML={highlightKeywords(full, highlights)}
          />
        </>
      )}
      <button
        className="mt-2 flex items-center text-blue-500"
        onClick={() => setExpanded(!expanded)} // 将展开状态取反
      >
        {expanded ? (
          <>
            收起全文
            <ChevronUp />
          </>
        ) : (
          <>
            展开全文
            <ChevronDown />
          </>
        )}
      </button>
    </div>
  );
};

// Pagination component
const Pagination: FC<{
  currentPage: number;
  totalPages: number;
  handlePageChange: (pageNumber: number) => void;
}> = ({ currentPage, totalPages, handlePageChange }) => {
  const maxVisibleButtons = 5; // 最大可见按钮数量
  let startPage = currentPage - Math.floor(maxVisibleButtons / 2);
  let endPage = currentPage + Math.ceil(maxVisibleButtons / 2) - 1;

  // 确保按钮不超出范围
  if (startPage < 1) {
    startPage = 1;
    endPage = Math.min(totalPages, startPage + maxVisibleButtons - 1);
  }
  if (endPage > totalPages) {
    endPage = totalPages;
    startPage = Math.max(1, endPage - maxVisibleButtons + 1);
  }

  const pageNumbers = Array.from(
    { length: endPage - startPage + 1 },
    (_, i) => startPage + i,
  );

  return (
    <div className="mt-4 flex justify-center">
      {startPage > 1 && (
        <button
          className={`mx-1 rounded-md bg-gray-200 px-3 py-1 text-gray-700`}
          onClick={() => handlePageChange(1)}
        >
          1
        </button>
      )}
      {startPage > 2 && <span className="mx-1">...</span>}
      {pageNumbers.map((pageNumber) => (
        <button
          key={pageNumber}
          className={`mx-1 rounded-md px-3 py-1 ${
            pageNumber === currentPage
              ? "bg-blue-500 text-white"
              : "bg-gray-200 text-gray-700"
          }`}
          onClick={() => handlePageChange(pageNumber)}
        >
          {pageNumber}
        </button>
      ))}
      {endPage < totalPages - 1 && <span className="mx-1">...</span>}
      {endPage < totalPages && (
        <button
          className={`mx-1 rounded-md bg-gray-200 px-3 py-1 text-gray-700`}
          onClick={() => handlePageChange(totalPages)}
        >
          {totalPages}
        </button>
      )}
    </div>
  );
};

// LawDocs component with pagination
const LawDocs: FC<{ documents: LawDocument[]; itemsPerPage: number }> = ({
  documents,
  itemsPerPage,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.ceil(documents.length / itemsPerPage);
  const paginationRef = useRef<HTMLDivElement>(null);

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = documents.slice(indexOfFirstItem, indexOfLastItem);

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
    paginationRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [currentPage]);

  return (
    <Wrapper
      title={
        <>
          <BookText></BookText> 检索结果 （共 {documents.length} 条）
        </>
      }
      content={
        <div className="grid grid-cols-1 gap-2">
          <div ref={paginationRef}>
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              handlePageChange={handlePageChange}
            />
          </div>
          {currentItems.map((document, index) => (
            <div key={index} className="mb-2">
              <LawDoc document={document} index={indexOfFirstItem + index} />
            </div>
          ))}
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            handlePageChange={handlePageChange}
          />
        </div>
      }
    ></Wrapper>
  );
};

export default LawDocs;
