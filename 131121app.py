import { useEffect, useRef, useState } from "react"

type Msg = {
  id: number
  user: "admin" | "fan"
  name: string
  avatar: string
  verified?: boolean
  text: string
  date: string
}

export default function App() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: 1,
      user: "admin",
      name: "아진",
      avatar: "https://i.pravatar.cc/100?img=5",
      verified: true,
      text: "안농 🙌🏻",
      date: "2025.12.18",
    },
    {
      id: 2,
      user: "admin",
      name: "아진",
      avatar: "https://i.pravatar.cc/100?img=5",
      verified: true,
      text: "올 한해도 벌써 끝이라는 사실이...",
      date: "2025.12.18",
    },
    {
      id: 3,
      user: "admin",
      name: "아진",
      avatar: "https://i.pravatar.cc/100?img=5",
      verified: true,
      text: "아쉽기도 하고 🥲 좋기도 해 ❤️",
      date: "2025.12.18",
    },
  ])

  const [input, setInput] = useState("")
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const send = () => {
    if (!input.trim()) return

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        user: "fan",
        name: "팬",
        avatar: "https://i.pravatar.cc/100?img=8",
        text: input,
        date: "2025.12.18",
      },
    ])
    setInput("")
  }

  let lastDate = ""

  return (
    <div className="h-screen bg-[#FFF5F5] flex justify-center">
      <div className="w-full max-w-[420px] flex flex-col">
        {/* 채팅 영역 */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {messages.map((m) => {
            const showDate = m.date !== lastDate
            lastDate = m.date

            return (
              <div key={m.id}>
                {showDate && (
                  <div className="flex justify-center my-4">
                    <div className="px-4 py-1 text-sm rounded-full bg-white shadow text-gray-600">
                      {m.date}
                    </div>
                  </div>
                )}

                <div className="flex gap-2 items-start">
                  <img
                    src={m.avatar}
                    className="w-9 h-9 rounded-full"
                  />

                  <div>
                    <div className="text-xs font-semibold flex items-center gap-1 mb-1">
                      {m.name}
                      {m.verified && (
                        <span className="text-red-400 text-xs">✔</span>
                      )}
                    </div>

                    <div
                      className="px-4 py-2 rounded-2xl text-white shadow max-w-[260px]"
                      style={{
                        background: m.user === "admin" ? "#D98989" : "#E5E5EA",
                        color: m.user === "admin" ? "white" : "#333",
                        wordBreak: "break-word",
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {m.text}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
          <div ref={bottomRef} />
        </div>

        {/* 입력창 */}
        <div className="p-3 border-t bg-white flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="메시지를 입력하세요"
            className="flex-1 px-4 py-2 rounded-full border outline-none"
          />
          <button
            onClick={send}
            className="px-4 rounded-full bg-[#D98989] text-white font-semibold"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  )
}


