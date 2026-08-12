import { Metadata } from "next";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

export const metadata: Metadata = {
  title: "Blog",
  description: "News, updates, and insights from the SupportGPT team.",
};

const posts = [
  {
    id: 1,
    title: "Introducing SupportGPT 2.0: The Next Generation of AI Support",
    excerpt: "Today we're thrilled to announce the biggest update to SupportGPT yet. With a completely rewritten RAG engine and our new Prompt Studio, building reliable AI agents has never been easier.",
    date: "Aug 11, 2026",
    category: "Product Updates",
    author: "Jane Doe",
    readTime: "5 min read",
    featured: true
  },
  {
    id: 2,
    title: "How to eliminate AI hallucinations in customer support",
    excerpt: "Hallucinations are the number one reason companies hesitate to deploy AI for customer support. Here is our technical approach to solving it using strict retrieval pipelines.",
    date: "Jul 28, 2026",
    category: "Engineering",
    author: "John Smith",
    readTime: "8 min read",
    featured: false
  },
  {
    id: 3,
    title: "The ROI of AI Support: A breakdown of cost savings",
    excerpt: "We analyzed over 10 million automated conversations to understand the true financial impact of deploying SupportGPT compared to traditional tiered support structures.",
    date: "Jul 15, 2026",
    category: "Customer Success",
    author: "Sarah Jenkins",
    readTime: "4 min read",
    featured: false
  },
  {
    id: 4,
    title: "SOC2 Type II Compliance Achieved",
    excerpt: "Security and privacy have always been our top priorities. Today we are proud to announce that SupportGPT is officially SOC2 Type II compliant.",
    date: "Jun 30, 2026",
    category: "Company",
    author: "Jane Doe",
    readTime: "2 min read",
    featured: false
  }
];

export default function BlogPage() {
  const featuredPost = posts.find(p => p.featured);
  const regularPosts = posts.filter(p => !p.featured);

  return (
    <div className="pb-24">
      <div className="pt-24 pb-16 text-center px-4 max-w-3xl mx-auto">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">The SupportGPT Blog</h1>
        <p className="text-xl text-muted-foreground">
          Thoughts on AI, customer success, engineering, and company updates.
        </p>
      </div>

      <div className="container px-4 md:px-6 max-w-6xl mx-auto">
        {/* Featured Post */}
        {featuredPost && (
          <Link href={`/blog/${featuredPost.id}`} className="group block mb-16">
            <div className="grid md:grid-cols-2 gap-8 bg-background border rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-all">
              <div className="bg-primary/5 aspect-[4/3] md:aspect-auto p-12 flex flex-col items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-blue-500/20 mix-blend-multiply"></div>
                <div className="w-32 h-32 bg-background rounded-2xl shadow-xl flex items-center justify-center relative z-10 transform group-hover:scale-105 transition-transform">
                  <span className="font-bold text-4xl text-primary">2.0</span>
                </div>
              </div>
              <div className="p-8 md:p-12 flex flex-col justify-center">
                <div className="flex items-center gap-4 mb-4">
                  <Badge>{featuredPost.category}</Badge>
                  <span className="text-sm text-muted-foreground">{featuredPost.date}</span>
                </div>
                <h2 className="text-3xl font-bold mb-4 group-hover:text-primary transition-colors">{featuredPost.title}</h2>
                <p className="text-muted-foreground text-lg mb-6 line-clamp-3">{featuredPost.excerpt}</p>
                <div className="flex items-center gap-3 mt-auto">
                  <div className="w-10 h-10 bg-zinc-200 rounded-full"></div>
                  <div>
                    <div className="text-sm font-medium">{featuredPost.author}</div>
                    <div className="text-xs text-muted-foreground">{featuredPost.readTime}</div>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        )}

        {/* Regular Posts Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {regularPosts.map((post) => (
            <Link key={post.id} href={`/blog/${post.id}`} className="group block h-full">
              <div className="bg-background border rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all h-full flex flex-col">
                <div className="aspect-video bg-muted relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-zinc-200 to-zinc-300"></div>
                </div>
                <div className="p-6 flex flex-col flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-xs font-semibold text-primary uppercase tracking-wider">{post.category}</span>
                    <span className="text-xs text-muted-foreground">• {post.date}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-3 group-hover:text-primary transition-colors">{post.title}</h3>
                  <p className="text-muted-foreground text-sm mb-6 line-clamp-3 flex-1">{post.excerpt}</p>
                  <div className="flex items-center gap-3 mt-auto border-t pt-4">
                    <div className="w-8 h-8 bg-zinc-200 rounded-full"></div>
                    <div>
                      <div className="text-sm font-medium">{post.author}</div>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
