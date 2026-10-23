// types.ts

export interface CodebaseContext {
  repoUrl: string;
  files: { path: string; content: string }[];
  sandboxLogs?: string;
}

export interface QuestionResponse {
  questionId: string;
  question: string;
  codeContextSnippet: string; // 针对的代码片段上下文
  targetConcept: string;      // 考察的技术概念（如并发控制、内存优化）
}

export interface EvaluationResult {
  score: number;             // 0 - 100
  isPassed: boolean;
  feedback: string;
  evidenceReferences: string[]; // 引用的代码或日志证据
  uncertaintyLevel: 'low' | 'medium' | 'high'; // 满足验收标准：标明不确定性
  disclaimer: string;        // 满足验收标准：明确声明不百分百证明源码所有权
}

export interface ExtractedSkill {
  skillName: string;         // 例如: "Rust Async Concurrency"
  proficiencyLevel: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  evidence: string;          // 支撑该技能的代码或答辩证据
}

export interface CollaboratorMatch {
  projectId: string;
  matchScore: number;
  matchType: 'similar' | 'complementary';
  matchingSkills: string[];
  projectSummary: string;
}
