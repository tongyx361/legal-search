import LawDocs from "@/app/components/lawdocs";
import LawDocument from "@/app/interfaces/lawdocument";
import { Annoyed, ArrowRight, ChevronDown, ChevronRight } from "lucide-react";
import { FC, useEffect, useRef, useState } from "react";

const rootUrl: string =
  process.env.NEXT_PUBLIC_ROOT_URL?.toString() || "http://localhost:8000";

const queryExpasionDelay: number = process.env
  .NEXT_PUBLIC_QUERY_EXPANSION_DELAY_MS
  ? Number(process.env.NEXT_PUBLIC_QUERY_EXPANSION_DELAY_MS)
  : 300; // 默认值

const nItemsPerPage: number = process.env.NEXT_PUBLIC_N_ITEMS_PER_PAGE
  ? Number(process.env.NEXT_PUBLIC_N_ITEMS_PER_PAGE)
  : 10; // 默认值

interface ToggleButtonProps {
  mode: string;
  isActive: boolean;
  onClick: () => void;
}

const ToggleButton: FC<ToggleButtonProps> = ({ mode, isActive, onClick }) => {
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

const fullRelatedQueries = [
  "婚姻法",
  "浙江润杭律师事务所",
  "婚姻法 AND 浙江润杭律师事务所 NOT 刑法",
  "有关机关和组织编印的仅供领导部门内部参阅的刊物、资料等刊登来信或者文章引起的名誉权纠纷，以及机关、社会团体、学术机构、企事业单位分发本单位、本系统或者其他一定范围内的一般内部刊物和内部资料所载内容引起的名誉权纠纷",
];

export const Search: FC = () => {
  const [value, setValue] = useState("");
  const [searchField, setSearchField] = useState("全文"); // 默认选择全文搜索字段
  const [fuzzySearch, setFuzzySearch] = useState(true); // 是否精确搜索
  const [judgeFilter, setJudgeFilter] = useState(""); // 法官过滤
  const [lawFilter, setLawFilter] = useState(""); // 法条过滤
  const [filterOpen, setFilterOpen] = useState(false); // 过滤框是否打开
  const [results, setResults] = useState<LawDocument[]>([]); // 搜索结果数据
  const [relatedQueries, setRelatedQueries] = useState<string[]>([]); // 相关搜索词
  const [searchFinished, setSearchFinished] = useState(false); // 搜索是否完成
  const [searchError, setSearchError] = useState(0); // 搜索错误

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const QueryContainer: FC<{ queries: string[] }> = ({ queries }) => {
    return (
      <div className="m-4 flex w-full flex-wrap items-center justify-center gap-4">
        {queries.map((query, index) => (
          <button
            key={index}
            className="flex-initial flex-wrap items-center justify-center rounded-lg border border-gray-200 bg-white p-2 text-xs font-medium text-gray-700 shadow-md hover:bg-gray-50 hover:text-gray-900"
            onClick={() => {
              // 修改 textarea 的值
              if (textareaRef.current) {
                textareaRef.current!.value +=
                  textareaRef.current!.value === "" ? query : ` ${query}`;
                // 创建模拟的 ChangeEvent 对象
                const event = new Event("input", { bubbles: true });
                Object.defineProperty(event, "target", {
                  value: textareaRef.current,
                });

                // 手动触发 handleInputChange
                handleInputChange(
                  event as unknown as React.ChangeEvent<HTMLTextAreaElement>,
                );
              }
            }}
          >
            {query}
          </button>
        ))}
      </div>
    );
  };

  const fetchRelatedQueries = async (query: string) => {
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
        // console.log("Related queries:", data.results);
        setRelatedQueries(data.results);
      } else {
        console.error("Failed to fetch related queries");
      }
    } catch (error) {
      console.error("Error fetching related queries:", error);
    }
  };

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

  const debouncedValue = useDebounce(value, queryExpasionDelay); // 500ms 的防抖延迟

  // 监听文本框输入事件，动态改变文本框的高度
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    const textarea = e.target;
    textarea.style.height = "1.5rem";
    textarea.style.height = textarea.scrollHeight + "px";
  };

  useEffect(() => {
    if (debouncedValue === "") {
      switch (searchField) {
        case "全文":
          setRelatedQueries(fullRelatedQueries);
          break;
        case "法官":
          setRelatedQueries(["张三", "张三 AND 李四 OR 王五 NOT 赵六"]);
          break;
        case "法条":
          setRelatedQueries([
            "婚姻法",
            "婚姻法 AND 民法典 OR 民法总则 NOT 刑法",
          ]);
          break;
      }
    } else fetchRelatedQueries(debouncedValue);
    // console.log("Debounced value:", debouncedValue);
  }, [debouncedValue, searchField]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (value) {
      setResults([]);
      setSearchFinished(false);
      setSearchError(0);
      let apiUrl: string = rootUrl;
      let requestData: { [key: string]: any } = {};
      let ndoc =
        !fuzzySearch || judgeFilter.length > 0 || lawFilter.length > 0 ? 1 : 20;
      let total_num: number = 0;

      switch (searchField) {
        case "全文":
          apiUrl += "/query";
          requestData = {
            query: value,
            mode: fuzzySearch ? "blurred" : "accurate",
            judge: judgeFilter,
            law: lawFilter,
            index: 0,
            ndoc: ndoc,
          };
          break;
        case "法官":
          apiUrl += "/query-judge";
          requestData = {
            query: value,
            index: 0,
            ndoc: ndoc,
          };
          break;
        case "法条":
          apiUrl += "/query-laws";
          requestData = {
            query: value,
            index: 0,
            ndoc: ndoc,
          };
          break;
        default:
          break;
      }

      try {
        do {
          const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
              // "X-API-Key": "",
              "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
            // mode: "no-cors",
          });

          if (response.ok) {
            const data = await response.json();
            const newResults = data.results;
            setSearchFinished(data.results.length === 0);
            // Update results state
            setResults((prevResults) => [...prevResults, ...newResults]);
            requestData.index = data.index.pop() + 1;
            total_num = data.total_num;
            // console.log("results.length:", results.length);
            // console.log("requestData.index:", requestData.index);
          } else {
            console.error("Failed to fetch results");
            setSearchError(response.status);
            break;
          }
          console.log("searchFinished:", searchFinished);
        } while (searchFinished);
        // console.log("searchFinished:", searchFinished);
      } catch (error) {
        console.error("Error fetching results:", error);
        setSearchError(1);
      }
    }
  };

  return (
    <div className="relative flex w-5/6 flex-col items-center justify-center">
      <div
        id="search-bar"
        className="relative w-5/6 flex-auto items-center justify-center gap-4"
      >
        <div
          role="group"
          aria-label="搜索字段"
          className="mb-2 w-48 flex-auto gap-4 rounded-t-lg bg-gray-200"
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
            mode="法官"
            isActive={searchField === "法官"}
            onClick={() => {
              setSearchField("法官");
              setRelatedQueries(["张三", "张三 AND 李四 OR 王五 NOT 赵六"]);
            }}
          />
          <ToggleButton
            mode="法条"
            isActive={searchField === "法条"}
            onClick={() => {
              setSearchField("法条");
              setRelatedQueries([
                "婚姻法",
                "婚姻法 AND 民法典 OR 民法总则 NOT 刑法",
              ]);
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
                  过滤
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
                value={value}
                autoFocus
                onChange={handleInputChange}
                placeholder="关键词/短句/长文本/表达式"
                className={`h-6 max-h-60 min-h-6 w-full flex-1 resize-y rounded-md bg-white px-2 pr-6 outline-none`}
              />
              <button
                type="button"
                className="inline-flex h-6 items-center justify-center rounded-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                onClick={() => setFuzzySearch(!fuzzySearch)}
              >
                {fuzzySearch ? "模糊" : "精确"}
              </button>
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
                    placeholder="张三 李四"
                    className="w-full rounded-md border px-2 py-1"
                    value={judgeFilter}
                    onChange={(e) => setJudgeFilter(e.target.value)}
                  />
                </div>
                <div className="flex items-center">
                  <span className="min-w-[4rem]">法条：</span>
                  <input
                    type="text"
                    placeholder="民法典 婚姻法"
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
