import {
  Annoyed,
  ArrowRight,
  BookText,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  Upload,
} from "lucide-react";
import { FC, useEffect, useRef, useState } from "react";

// Environment variables
const rootUrl: string =
  process.env.NEXT_PUBLIC_ROOT_URL?.toString() || "http://localhost:5678";

const queryExpasionDelay: number = process.env
  .NEXT_PUBLIC_QUERY_EXPANSION_DELAY_MS
  ? Number(process.env.NEXT_PUBLIC_QUERY_EXPANSION_DELAY_MS)
  : 300;

const nItemsPerPage: number = process.env.NEXT_PUBLIC_N_ITEMS_PER_PAGE
  ? Number(process.env.NEXT_PUBLIC_N_ITEMS_PER_PAGE)
  : 10;

// Interfaces
interface LawDocument {
  title: string;
  full: string;
  laws: string[];
  judges: string[];
  keywords: string[];
  highlights: string[];
  expanded: boolean;
}

export const Search: FC = () => {
  // State variables
  const [value, setValue] = useState("");
  const [searchField, setSearchField] = useState("全文"); // 默认选择全文搜索字段
  const [fuzzySearch, setFuzzySearch] = useState(true); // 是否精确搜索
  const [judgeFilter, setJudgeFilter] = useState(""); // 法官过滤
  const [lawFilter, setLawFilter] = useState(""); // 法条过滤
  const [filterOpen, setFilterOpen] = useState(false); // 过滤框是否打开
  const [results, setResults] = useState<any[]>([]); // 搜索结果数据
  const [relatedQueries, setRelatedQueries] = useState<string[]>([]); // 相关搜索词
  const [searchFinished, setSearchFinished] = useState(false); // 搜索是否完成
  const [searchError, setSearchError] = useState(0); // 搜索错误
  const [currentPage, setCurrentPage] = useState(1);
  const [fileName, setFileName] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // References
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Components and utilies

  const ToggleButton: FC<{
    mode: string;
    isActive: boolean;
    onClick: () => void;
  }> = ({ mode, isActive, onClick }) => {
    return (
      <button
        role="switch"
        aria-checked={isActive}
        className={`rounded-t-lg px-4 py-2 ${isActive ? "bg-black text-white" : ""}`}
        onClick={onClick}
      >
        {mode}
      </button>
    );
  };

  const handleInputChange = () => {
    setFileName("");

    if (textareaRef.current) {
      setValue(textareaRef.current.value); // Dynamic textarea height
      textareaRef.current.style.height = "1.5rem";
      textareaRef.current.style.height =
        textareaRef.current.scrollHeight + "px";
    }
  };

  // Query recommendation and expansion

  const fullRelatedQueries = [
    "婚姻法",
    "婚姻法 AND 浙江润杭律师事务所",
    "婚姻法 AND 浙江润杭律师事务所 AND NOT 2016",
  ];

  const judgeRelatedQueries = ["夏明贵", "夏明贵 王杨沁如"];

  const lawRelatedQueries = ["中华人民共和国民事诉讼法", "民事诉讼法 合同法"];

  const QueryContainer: FC<{ queries: string[] }> = ({ queries }) => {
    return (
      <div className="m-4 flex w-full flex-wrap items-center justify-center gap-4">
        {queries.map((query, index) => (
          <button
            key={index}
            className="flex-initial flex-wrap items-center justify-center rounded-lg border border-gray-200 bg-white p-2 text-xs font-medium text-gray-700 shadow-md hover:bg-gray-50 hover:text-gray-900"
            onClick={() => {
              textareaRef.current!.value = query; // Replace
              // textareaRef.current!.value +=
              // textareaRef.current!.value === "" ? query : ` ${query}`; // Append
              handleInputChange();
            }}
          >
            {query}
          </button>
        ))}
      </div>
    );
  };

  const checkIfChinese = (text: string) => {
    const chineseRegex = /^[\u4e00-\u9fa5\sANDORNOT]+$/;
    return chineseRegex.test(text);
  };

  const fetchRelatedQueries = async (query: string) => {
    if (!checkIfChinese(query)) return;
    try {
      const response = await fetch(rootUrl + "/expand", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query }),
      });

      if (response.ok) {
        const data = await response.json();
        if (textareaRef.current?.value !== "") setRelatedQueries(data.results);
      } else {
        console.error("Failed to fetch related queries");
      }
    } catch (error) {
      console.error("Error fetching related queries:", error);
    }
  };

  // Debounce

  const useDebounce = (value: any, delay: number) => {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedValue(value);
      }, delay);

      return () => {
        clearTimeout(handler);
      };
    }, [value, delay]);

    return debouncedValue;
  };

  const debouncedValue = useDebounce(value, queryExpasionDelay);

  useEffect(() => {
    if (debouncedValue === "") {
      switch (searchField) {
        case "全文":
          setRelatedQueries(fullRelatedQueries);
          break;
        case "法官（模糊）":
          setRelatedQueries(judgeRelatedQueries);
          break;
        case "法条（模糊）":
          setRelatedQueries(lawRelatedQueries);
          break;
      }
    } else {
      console.log("debouncedValue:", debouncedValue);
      console.log("fileName:", fileName);
      if (!fileName) {
        if (searchField === "全文") fetchRelatedQueries(debouncedValue);
      } else setRelatedQueries([]);
    }
  }, [debouncedValue]);

  const initSearch = () => {
    setResults([]);
    setSearchFinished(false);
    setSearchError(0);
    setCurrentPage(1);
  };

  const fetchData = async (
    searchField: string,
    value: string,
    fuzzySearch: boolean,
    judgeFilter: string,
    lawFilter: string,
  ) => {
    if (isSubmitting && abortControllerRef.current) {
      console.log("Aborting previous search with", abortControllerRef.current);
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    const sig = abortControllerRef.current.signal;
    setIsSubmitting(true);

    initSearch();
    let apiUrl: string = rootUrl;
    let ndoc = 1;

    let requestData: { [key: string]: any } = {
      query: value,
      index: 0,
      ndoc: ndoc,
    };

    switch (searchField) {
      case "全文":
        apiUrl += "/query";
        requestData = {
          ...requestData,
          mode: fuzzySearch ? "blurred" : "accurate",
          judge: judgeFilter,
          law: lawFilter,
        };
        break;
      case "法官（模糊）":
        apiUrl += "/query-judge";
        break;
      case "法条（模糊）":
        apiUrl += "/query-laws";
        break;
      default:
        break;
    }

    let total_num: number = 0;
    let end_search = false;
    try {
      do {
        console.log("apiUrl:", apiUrl);
        console.log("requestData:", requestData);
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestData),
        });

        if (response.ok) {
          const data = await response.json();
          console.log("data:", data);
          let newResults = data.results;
          for (let i = 0; i < newResults.length; i++) {
            newResults[i].expanded = false;
          }

          if (data.results.length === 0) {
            end_search = true;
            setSearchFinished(true);
          }

          if (sig.aborted) {
            console.log("Aborted by", abortControllerRef.current);
            setResults([]);
            throw "aborted";
          }
          // Update results state
          setResults((prevResults) => [...prevResults, ...newResults]);
          if (data.index.length > 0) requestData.index = data.index.pop() + 1;
          requestData.ndoc = 2 * requestData.ndoc;
          total_num = data.total_num;
          // console.log("results.length:", results.length);
          // console.log("requestData.index:", requestData.index);
        } else {
          console.error("Failed to fetch results");
          setSearchError(response.status);
          break;
        }
      } while (!end_search);
      // console.log("searchFinished:", searchFinished);
    } catch (error) {
      if (error !== "aborted") {
        console.error("Error fetching results:", error);
        setSearchError(1);
      }
    }
    setIsSubmitting(false);
    abortControllerRef.current = null;
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (value)
      fetchData(searchField, value, fuzzySearch, judgeFilter, lawFilter);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    if (e.target.files.length === 0) return;
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      const file_str = e.target?.result as string;
      const file_str_chn = file_str.match(/[\u4e00-\u9fa5]+/g)?.join("") || "";
      setValue(file_str_chn);
      setFileName(file.name);
    };
    reader.readAsText(file);
  };

  // Component to display a single law document
  const LawDoc: FC<{ document: LawDocument }> = ({ document }) => {
    const [expanded, setExpanded] = useState(document.expanded);

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

    const SimilarSearch: FC = () => {
      return (
        <div className="flex">
          <button
            className="m-2 flex items-center rounded-md border bg-green-200 p-2"
            onClick={() => {
              const searchField = "全文";
              setSearchField(searchField);
              const query = document.full;
              setFuzzySearch(true);
              setJudgeFilter("");
              setLawFilter("");
              setFilterOpen(false);
              textareaRef.current!.value = query;
              handleInputChange();
              fetchData(searchField, query, true, "", "");
            }}
          >
            相似案例
          </button>
          <button
            className="m-2 flex items-center rounded-md border bg-blue-200 p-2"
            onClick={() => {
              const searchField = "法官（模糊）";
              setSearchField(searchField);
              const query = document.judges.join(" ");
              setValue(query);
              textareaRef.current!.value = query;
              handleInputChange();
              fetchData(searchField, query, true, "", "");
            }}
          >
            相似法官案例
          </button>
          <button
            className="m-2 flex items-center rounded-md border bg-teal-200 p-2"
            onClick={() => {
              const searchField = "法条（模糊）";
              setSearchField(searchField);
              const query = document.laws.join(" ");
              setValue(query);
              textareaRef.current!.value = query;
              handleInputChange();
              fetchData(searchField, query, true, "", "");
            }}
          >
            相似法条案例
          </button>
        </div>
      );
    };

    const ExpandButton: FC = () => {
      return (
        <button
          className="mt-2 flex items-center text-blue-500"
          onClick={() => {
            setExpanded(!expanded);
            document.expanded = !document.expanded;
          }}
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
      );
    };

    return (
      <div className="mb-4 flex flex-col items-center rounded-md border border-gray-300 bg-gray-50 p-4">
        <div
          id="doc-header"
          className="items-left justify-left m-1 flex w-full flex-col"
        >
          <h3 className="mb-2 text-lg font-semibold">{document.title}</h3>
          <CustomList
            prompt="法官："
            items={document.judges}
            itemColor="bg-blue-200 text-blue-800"
          />
          <CustomList
            prompt="法条："
            items={document.laws}
            itemColor="bg-teal-200 text-teal-800"
          />
          <CustomList
            prompt="关键词："
            items={document.keywords}
            itemColor="bg-gray-200 text-gray-800"
          />
        </div>
        {expanded && (
          <>
            <SimilarSearch />
            <ExpandButton />
            <div
              className="m-2 w-full rounded-md border bg-white p-2 text-sm leading-6"
              dangerouslySetInnerHTML={highlightKeywords(
                document.full,
                document.highlights,
              )}
            ></div>
          </>
        )}
        <SimilarSearch />
        <ExpandButton />
      </div>
    );
  };

  // Component of search results with pagination
  const LawDocs: FC<{ documents: LawDocument[]; itemsPerPage: number }> = ({
    documents,
    itemsPerPage,
  }) => {
    const totalPages = Math.ceil(documents.length / itemsPerPage);
    const paginationRef = useRef<HTMLDivElement>(null);

    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = documents.slice(indexOfFirstItem, indexOfLastItem);

    const handlePageChange = (pageNumber: number) => {
      setCurrentPage(pageNumber);
      paginationRef.current?.scrollIntoView({ behavior: "smooth" });
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

    return (
      <div className="flex w-full flex-col gap-4">
        <div className="flex gap-2 text-blue-500">
          {
            <>
              <BookText></BookText> 检索结果
              {searchFinished ? `（共 ${documents.length} 条）` : ""}
            </>
          }
        </div>
        {
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
                <LawDoc document={document} />
              </div>
            ))}
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              handlePageChange={handlePageChange}
            />
          </div>
        }
      </div>
    );
  };

  // Main search bar component
  return (
    <div className="relative flex w-5/6 flex-col items-center justify-center">
      <div
        id="search-bar"
        className="relative w-5/6 flex-auto items-center justify-center gap-4"
      >
        <div
          role="group"
          aria-label="搜索字段"
          className="mb-2 w-80 flex-row flex-nowrap gap-4 rounded-t-lg bg-gray-200"
        >
          <ToggleButton
            mode="全文"
            isActive={searchField === "全文"}
            onClick={() => {
              setSearchField("全文");
              setRelatedQueries(fullRelatedQueries);
            }}
          />
          <ToggleButton
            mode="法官（模糊）"
            isActive={searchField === "法官（模糊）"}
            onClick={() => {
              setSearchField("法官（模糊）");
              setRelatedQueries(judgeRelatedQueries);
            }}
          />
          <ToggleButton
            mode="法条（模糊）"
            isActive={searchField === "法条（模糊）"}
            onClick={() => {
              setSearchField("法条（模糊）");
              setRelatedQueries(lawRelatedQueries);
            }}
          />
        </div>

        <div className="items-center justify-center gap-4">
          <form onSubmit={handleSubmit}>
            <div className="flex min-w-[800px] items-start justify-center gap-2 rounded-lg border bg-white px-2 py-2 ring-8 ring-zinc-300/20 focus-within:border-zinc-300">
              {searchField === "全文" && (
                <button
                  type="button"
                  className="w-17 inline-flex h-6 items-center justify-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  onClick={() => setFilterOpen(!filterOpen)}
                >
                  精确过滤
                  {filterOpen ? (
                    <ChevronDown size={16} />
                  ) : (
                    <ChevronRight size={16} />
                  )}
                </button>
              )}
              <textarea
                id="query-input"
                ref={textareaRef}
                value={fileName || value}
                autoFocus
                onChange={handleInputChange}
                placeholder={fileName || "关键词/短句/长文本/表达式"}
                className="h-6 max-h-60 min-h-6 w-full flex-1 resize-y rounded-md bg-white px-2 pr-6 outline-none"
              />
              {searchField === "全文" && (
                <div>
                  <button
                    type="button"
                    className="w-17 inline-flex h-6 items-center justify-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    onClick={() =>
                      document.getElementById("fileInput")?.click()
                    }
                  >
                    <Upload size={16} className="mr-2" />
                    上传文档
                  </button>
                  <input
                    type="file"
                    id="fileInput"
                    style={{ display: "none" }}
                    onChange={handleFileUpload}
                  />
                </div>
              )}
              {searchField === "全文" && (
                <button
                  type="button"
                  className="inline-flex h-6 items-center justify-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  onClick={() => setFuzzySearch(!fuzzySearch)}
                >
                  {fuzzySearch ? "模糊" : "精确"}
                </button>
              )}
              <button
                type="submit"
                className="relative w-auto overflow-hidden rounded-xl border border-black bg-black fill-white px-2 py-1 text-white active:scale-95"
              >
                <ArrowRight size={16} />
              </button>
            </div>
            {searchField === "全文" && filterOpen && (
              <div className="relative z-10 mt-2 flex w-full flex-col gap-2 rounded-md border border-gray-300 bg-white px-2 py-1">
                <div className="flex items-center">
                  <span className="min-w-[4rem]">法官：</span>
                  <input
                    type="text"
                    placeholder="张三 AND 李四"
                    className="w-full rounded-md border px-2 py-1"
                    value={judgeFilter}
                    onChange={(e) => setJudgeFilter(e.target.value)}
                  />
                </div>
                <div className="flex items-center">
                  <span className="min-w-[4rem]">法条：</span>
                  <input
                    type="text"
                    placeholder="婚姻法 AND 诉讼法"
                    className="w-full rounded-md border px-2 py-1"
                    value={lawFilter}
                    onChange={(e) => setLawFilter(e.target.value)}
                  />
                </div>
              </div>
            )}
          </form>
        </div>
        <QueryContainer queries={relatedQueries} />
      </div>
      {results.length > 0 ? (
        <LawDocs documents={results} itemsPerPage={nItemsPerPage} />
      ) : (
        <div>
          {searchFinished && (
            <div className="flex gap-4 rounded bg-white p-4 font-medium text-blue-500 shadow-xl">
              <Annoyed></Annoyed>
              {searchError === 0 ? `没有找到相关文书` : `搜索出错，请重试`}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
