"use client";

import * as React from "react"
import { Check, X } from "lucide-react"

import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface MultiSelectProps {
    options: { label: string; value: string }[]
    selected: string[]
    onChange: (selected: string[]) => void
    placeholder?: string
    className?: string
}

export function MultiSelect({
    options,
    selected,
    onChange,
    placeholder = "Select items...",
    className,
}: MultiSelectProps) {
    const [isOpen, setIsOpen] = React.useState(false)
    const containerRef = React.useRef<HTMLDivElement>(null)

    // Close dropdown when clicking outside
    React.useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleSelect = (value: string) => {
        const newSelected = selected.includes(value)
            ? selected.filter((item) => item !== value)
            : [...selected, value]
        onChange(newSelected)
    }

    const handleRemove = (value: string, e: React.MouseEvent) => {
        e.stopPropagation()
        onChange(selected.filter((item) => item !== value))
    }

    return (
        <div ref={containerRef} className={cn("relative", className)}>
            <Button
                type="button"
                variant="outline"
                role="combobox"
                aria-expanded={isOpen}
                onClick={() => setIsOpen(!isOpen)}
                className="w-full justify-between min-h-10"
            >
                <div className="flex gap-1 flex-wrap">
                    {selected.length > 0 ? (
                        selected.map((value) => {
                            const option = options.find((opt) => opt.value === value)
                            return (
                                <Badge
                                    variant="secondary"
                                    key={value}
                                    className="mr-1"
                                    onClick={(e) => handleRemove(value, e)}
                                >
                                    {option?.label || value}
                                    <X className="ml-1 h-3 w-3 cursor-pointer" />
                                </Badge>
                            )
                        })
                    ) : (
                        <span className="text-muted-foreground">{placeholder}</span>
                    )}
                </div>
            </Button>

            {isOpen && (
                <div className="absolute z-[100] mt-1 w-full rounded-md border border-border bg-background shadow-lg">
                    <div className="max-h-60 overflow-auto p-1">
                        {options.length === 0 ? (
                            <div className="px-2 py-1.5 text-sm text-muted-foreground">No options available</div>
                        ) : (
                            options.map((option) => (
                                <div
                                    key={option.value}
                                    onClick={() => handleSelect(option.value)}
                                    className={cn(
                                        "flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm hover:bg-accent",
                                        selected.includes(option.value) && "bg-accent"
                                    )}
                                >
                                    <div className={cn(
                                        "mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary",
                                        selected.includes(option.value) ? "bg-primary text-primary-foreground" : "opacity-50"
                                    )}>
                                        {selected.includes(option.value) && <Check className="h-3 w-3" />}
                                    </div>
                                    {option.label}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
