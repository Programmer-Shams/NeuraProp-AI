"use client";

import { useState } from "react";
import {
  FileText,
  Upload,
  Search,
  Plus,
  MoreVertical,
  Trash2,
  Edit3,
  Eye,
  BookOpen,
  HelpCircle,
  Clock,
  CheckCircle2,
  AlertCircle,
  ChevronDown,
  FileUp,
  X,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// --- Mock Data ---

interface Document {
  id: string;
  name: string;
  type: string;
  category: string;
  chunks: number;
  status: "indexed" | "processing" | "failed";
  uploadedAt: string;
  size: string;
}

interface FAQ {
  id: string;
  question: string;
  answer: string;
  category: string;
  hits: number;
  lastUpdated: string;
}

const documents: Document[] = [
  { id: "doc-1", name: "Trading Rules & Guidelines v3.2", type: "PDF", category: "Rules", chunks: 48, status: "indexed", uploadedAt: "Mar 15, 2026", size: "2.4 MB" },
  { id: "doc-2", name: "Payout Policy & Procedures", type: "PDF", category: "Payout", chunks: 32, status: "indexed", uploadedAt: "Mar 12, 2026", size: "1.8 MB" },
  { id: "doc-3", name: "Challenge Account Terms", type: "PDF", category: "Onboarding", chunks: 24, status: "indexed", uploadedAt: "Mar 10, 2026", size: "980 KB" },
  { id: "doc-4", name: "MT5 Platform Guide", type: "PDF", category: "Technical", chunks: 56, status: "indexed", uploadedAt: "Mar 8, 2026", size: "3.1 MB" },
  { id: "doc-5", name: "cTrader Setup Instructions", type: "DOCX", category: "Technical", chunks: 18, status: "indexed", uploadedAt: "Mar 5, 2026", size: "720 KB" },
  { id: "doc-6", name: "KYC Compliance Requirements", type: "PDF", category: "Compliance", chunks: 0, status: "processing", uploadedAt: "Apr 6, 2026", size: "1.2 MB" },
  { id: "doc-7", name: "Refund & Billing Policy", type: "PDF", category: "Billing", chunks: 16, status: "indexed", uploadedAt: "Feb 28, 2026", size: "540 KB" },
];

const faqs: FAQ[] = [
  { id: "faq-1", question: "How do I request a payout from my funded account?", answer: "To request a payout, navigate to your dashboard and click 'Request Withdrawal'. You must have completed at least 5 trading days and your account must be in profit. Payouts are processed within 1-3 business days.", category: "Payout", hits: 342, lastUpdated: "Mar 20, 2026" },
  { id: "faq-2", question: "What is the maximum daily loss limit?", answer: "The maximum daily loss limit is 5% of your initial account balance. This includes both realized and unrealized losses. If breached, your account will be suspended for review.", category: "Rules", hits: 287, lastUpdated: "Mar 18, 2026" },
  { id: "faq-3", question: "How long does KYC verification take?", answer: "KYC verification typically takes 5-15 minutes using our automated Veriff system. In some cases, manual review may be required which can take up to 24 hours.", category: "Account", hits: 198, lastUpdated: "Mar 15, 2026" },
  { id: "faq-4", question: "Can I hold positions over the weekend?", answer: "Weekend holding is allowed on all account types except during the evaluation phase. Funded accounts may hold weekend positions with a maximum exposure of 50% of the normal position size limit.", category: "Rules", hits: 176, lastUpdated: "Mar 22, 2026" },
  { id: "faq-5", question: "What trading platforms do you support?", answer: "We support MetaTrader 4 (MT4), MetaTrader 5 (MT5), cTrader, Match-Trader, and TradeLocker. Each platform has specific setup guides available in our knowledge base.", category: "Technical", hits: 156, lastUpdated: "Mar 10, 2026" },
  { id: "faq-6", question: "How do I reset my challenge account?", answer: "You can request an account reset through the support channel. A reset will restore your account to its initial balance. Note: there is a $50 reset fee, and you'll need to restart your trading day count.", category: "Account", hits: 134, lastUpdated: "Apr 1, 2026" },
];

const statusConfig: Record<string, { variant: "success" | "warning" | "danger"; icon: React.ComponentType<{ className?: string }> }> = {
  indexed: { variant: "success", icon: CheckCircle2 },
  processing: { variant: "warning", icon: Clock },
  failed: { variant: "danger", icon: AlertCircle },
};

export default function KnowledgeBasePage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [faqSearch, setFaqSearch] = useState("");

  const totalChunks = documents.reduce((sum, d) => sum + d.chunks, 0);
  const indexedDocs = documents.filter((d) => d.status === "indexed").length;

  const filteredDocs = documents.filter(
    (d) => !searchQuery || d.name.toLowerCase().includes(searchQuery.toLowerCase()) || d.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredFaqs = faqs.filter(
    (f) => !faqSearch || f.question.toLowerCase().includes(faqSearch.toLowerCase()) || f.category.toLowerCase().includes(faqSearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Knowledge Base</h1>
        <p className="text-sm text-[var(--muted-foreground)]">
          Manage documents, FAQs, and rules that power your AI agents
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-950">
              <FileText className="h-5 w-5 text-brand-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{documents.length}</p>
              <p className="text-xs text-[var(--muted-foreground)]">Documents</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 dark:bg-emerald-950">
              <BookOpen className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{totalChunks}</p>
              <p className="text-xs text-[var(--muted-foreground)]">Indexed Chunks</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 dark:bg-violet-950">
              <HelpCircle className="h-5 w-5 text-violet-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{faqs.length}</p>
              <p className="text-xs text-[var(--muted-foreground)]">FAQs</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 dark:bg-amber-950">
              <CheckCircle2 className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{Math.round((indexedDocs / documents.length) * 100)}%</p>
              <p className="text-xs text-[var(--muted-foreground)]">Indexed</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="documents" className="space-y-4">
        <TabsList>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="faqs">FAQs</TabsTrigger>
        </TabsList>

        {/* Documents Tab */}
        <TabsContent value="documents" className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
              <Input placeholder="Search documents..." className="pl-9" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </div>
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Upload className="mr-1.5 h-4 w-4" />
                  Upload Document
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Upload Document</DialogTitle>
                  <DialogDescription>Upload a PDF, DOCX, or TXT file. It will be automatically chunked and indexed for RAG retrieval.</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-[var(--border)] p-8 text-center">
                    <FileUp className="h-10 w-10 text-[var(--muted-foreground)]" />
                    <p className="mt-2 text-sm font-medium">Drop your file here or click to browse</p>
                    <p className="mt-1 text-xs text-[var(--muted-foreground)]">PDF, DOCX, TXT up to 10MB</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Category</label>
                    <Select>
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="rules">Rules</SelectItem>
                        <SelectItem value="payout">Payout</SelectItem>
                        <SelectItem value="technical">Technical</SelectItem>
                        <SelectItem value="compliance">Compliance</SelectItem>
                        <SelectItem value="billing">Billing</SelectItem>
                        <SelectItem value="onboarding">Onboarding</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline">Cancel</Button>
                  <Button>Upload & Index</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="space-y-2">
            {filteredDocs.map((doc) => {
              const status = statusConfig[doc.status];
              const StatusIcon = status.icon;
              return (
                <Card key={doc.id}>
                  <CardContent className="flex items-center gap-4 p-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--muted)]">
                      <FileText className="h-5 w-5 text-[var(--muted-foreground)]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium truncate">{doc.name}</p>
                        <Badge variant={status.variant} className="text-[10px] shrink-0">
                          <StatusIcon className="mr-1 h-3 w-3" />
                          {doc.status}
                        </Badge>
                      </div>
                      <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">
                        {doc.type} &middot; {doc.size} &middot; {doc.category} &middot; {doc.chunks} chunks &middot; Uploaded {doc.uploadedAt}
                      </p>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="shrink-0">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem><Eye className="mr-2 h-4 w-4" />Preview</DropdownMenuItem>
                        <DropdownMenuItem><Edit3 className="mr-2 h-4 w-4" />Re-index</DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="text-red-600"><Trash2 className="mr-2 h-4 w-4" />Delete</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* FAQs Tab */}
        <TabsContent value="faqs" className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
              <Input placeholder="Search FAQs..." className="pl-9" value={faqSearch} onChange={(e) => setFaqSearch(e.target.value)} />
            </div>
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-1.5 h-4 w-4" />
                  Add FAQ
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add FAQ</DialogTitle>
                  <DialogDescription>Add a frequently asked question. The AI will use this for instant, accurate responses.</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div>
                    <label className="text-sm font-medium">Question</label>
                    <Input className="mt-1" placeholder="What do traders commonly ask?" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Answer</label>
                    <Textarea className="mt-1" placeholder="Provide a comprehensive answer..." rows={4} />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Category</label>
                    <Select>
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="payout">Payout</SelectItem>
                        <SelectItem value="rules">Rules</SelectItem>
                        <SelectItem value="account">Account</SelectItem>
                        <SelectItem value="technical">Technical</SelectItem>
                        <SelectItem value="billing">Billing</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline">Cancel</Button>
                  <Button>Save FAQ</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="space-y-3">
            {filteredFaqs.map((faq) => (
              <Card key={faq.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <HelpCircle className="h-4 w-4 shrink-0 text-brand-500" />
                        <p className="text-sm font-medium">{faq.question}</p>
                      </div>
                      <p className="mt-2 text-sm text-[var(--muted-foreground)] line-clamp-2 pl-6">
                        {faq.answer}
                      </p>
                      <div className="mt-2 flex items-center gap-3 pl-6">
                        <Badge variant="outline" className="text-[10px]">{faq.category}</Badge>
                        <span className="text-[10px] text-[var(--muted-foreground)]">{faq.hits} hits</span>
                        <span className="text-[10px] text-[var(--muted-foreground)]">Updated {faq.lastUpdated}</span>
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="shrink-0">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem><Edit3 className="mr-2 h-4 w-4" />Edit</DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="text-red-600"><Trash2 className="mr-2 h-4 w-4" />Delete</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
