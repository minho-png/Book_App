"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, Database, Brain, CheckCircle2 } from "lucide-react"

const steps = [
  { icon: Search, text: "교보문고 랭킹 검색 중...", duration: 1200 },
  { icon: Database, text: "알라딘 데이터 분석 중...", duration: 1000 },
  { icon: Database, text: "밀리의서재 랭킹 수집 중...", duration: 1100 },
  { icon: Brain, text: "사용자 취향 분석 중...", duration: 900 },
  { icon: CheckCircle2, text: "추천 결과 생성 완료!", duration: 600 },
]

export function RAGLoading({ onComplete }: { onComplete?: () => void }) {
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    if (currentStep >= steps.length) {
      onComplete?.()
      return
    }

    const timer = setTimeout(() => {
      setCurrentStep((prev) => prev + 1)
    }, steps[currentStep].duration)

    return () => clearTimeout(timer)
  }, [currentStep, onComplete])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col gap-2 py-3"
    >
      <div className="flex items-center gap-2 mb-1">
        <div className="relative h-4 w-4">
          <motion.div
            className="absolute inset-0 rounded-full bg-accent/30"
            animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0.2, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <div className="absolute inset-0.5 rounded-full bg-accent" />
        </div>
        <span className="text-xs font-medium text-foreground">
          데이터베이스 스캔 중...
        </span>
      </div>

      <div className="flex flex-col gap-1.5 pl-1">
        <AnimatePresence>
          {steps.slice(0, currentStep + 1).map((step, i) => {
            const Icon = step.icon
            const isComplete = i < currentStep
            const isCurrent = i === currentStep

            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className="flex items-center gap-2"
              >
                <Icon
                  className={`h-3.5 w-3.5 ${
                    isComplete
                      ? "text-[#7BA08A]"
                      : isCurrent
                        ? "text-accent"
                        : "text-muted-foreground"
                  }`}
                />
                <span
                  className={`text-[11px] ${
                    isComplete
                      ? "text-muted-foreground line-through"
                      : isCurrent
                        ? "text-foreground font-medium"
                        : "text-muted-foreground"
                  }`}
                >
                  {step.text}
                </span>
                {isCurrent && !isComplete && (
                  <motion.div
                    className="h-1 w-1 rounded-full bg-accent"
                    animate={{ opacity: [1, 0.3, 1] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                  />
                )}
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
