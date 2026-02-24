"use client"

import { motion } from "framer-motion"
import { Database } from "lucide-react"

export interface SourceData {
  store: "kyobo" | "millie" | "aladdin"
  category: string
  confidence: number
}

const storeConfig: Record<string, { label: string; color: string; bgColor: string }> = {
  kyobo: { label: "교보문고", color: "#C4956A", bgColor: "rgba(196,149,106,0.12)" },
  millie: { label: "밀리의서재", color: "#7BA08A", bgColor: "rgba(123,160,138,0.12)" },
  aladdin: { label: "알라딘", color: "#5B8FA8", bgColor: "rgba(91,143,168,0.12)" },
}

export function SourceCitation({ source }: { source: SourceData }) {
  const config = storeConfig[source.store]

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium border"
      style={{
        backgroundColor: config.bgColor,
        color: config.color,
        borderColor: `${config.color}30`,
      }}
    >
      <Database className="h-3 w-3" />
      {config.label} - {source.category}
      <span className="opacity-60">{source.confidence}%</span>
    </motion.span>
  )
}

export function SourceCitationGroup({ sources }: { sources: SourceData[] }) {
  return (
    <div className="flex flex-wrap gap-1.5 mt-2">
      {sources.map((source, i) => (
        <SourceCitation key={`${source.store}-${i}`} source={source} />
      ))}
    </div>
  )
}
