export type DownloadItem = {
  label: string;
  description: string;
  file: string;
  format: string;
};

export type DownloadGroup = {
  title: string;
  description: string;
  featured?: boolean;
  items: DownloadItem[];
};

export const downloadGroups: DownloadGroup[] = [
  {
    title: "Choose one edition",
    description: "Do not mix them. Kairali staff use the employee edition. Everyone else uses the company-neutral reusable edition.",
    featured: true,
    items: [
      {
        label: "Kairali employee edition",
        description: "Workspace, Kairali Setup Helper, role prompts, homework workers, opt-in skills and lifecycle controls.",
        file: "KAIRALI-AI-HUMAN-v200-EMPLOYEE-EDITION-PUBLIC-KIT.zip",
        format: "ZIP",
      },
      {
        label: "Kairali edition checksum",
        description: "Use this when the Setup Helper or IT verifies the exact employee-edition download.",
        file: "KAIRALI-AI-HUMAN-v200-EMPLOYEE-EDITION-PUBLIC-KIT.zip.sha256",
        format: "SHA-256",
      },
      {
        label: "Reusable edition",
        description: "Company-neutral workspace, generic Setup Helper and lifecycle controls with no Kairali employee content.",
        file: "AI-HUMAN-v200-REUSABLE-EDITION-PUBLIC-KIT.zip",
        format: "ZIP",
      },
      {
        label: "Reusable edition checksum",
        description: "Use this when the Setup Helper verifies the exact company-neutral download.",
        file: "AI-HUMAN-v200-REUSABLE-EDITION-PUBLIC-KIT.zip.sha256",
        format: "SHA-256",
      },
    ],
  },
  {
    title: "User start",
    description: "Start here if you are setting up your own AI-human worker; company employees and external users follow the same identity-and-Gate-0 check.",
    items: [
      {
        label: "Setup and proof guide",
        description: "The simple user path for Mac and Windows.",
        file: "EMPLOYEE-SETUP-AND-PROOF-GUIDE-v7-PUBLIC-KIT.pdf",
        format: "PDF",
      },
      {
        label: "Editable setup guide",
        description: "The same guide in an editable document.",
        file: "EMPLOYEE-SETUP-AND-PROOF-GUIDE-v7-PUBLIC-KIT.docx",
        format: "DOCX",
      },
      {
        label: "Setup Helper card",
        description: "The exact rescue prompt to use whenever setup gets stuck.",
        file: "SETUP-HELPER-CARD-v7-PUBLIC-KIT.pdf",
        format: "PDF",
      },
      {
        label: "Role mission workbook",
        description: "Choose one approved mission and name its proof.",
        file: "ROLE-MISSION-WORKBOOK-v8-PUBLIC-KIT.pdf",
        format: "PDF",
      },
    ],
  },
  {
    title: "Managed updates",
    description: "Check first, approve at a safe checkpoint, then keep the receipt.",
    items: [
      {
        label: "Kairali managed update workflow",
        description: "The exact beginner and technical path, including GitHub Desktop, preservation, rollback and Monitor proof.",
        file: "KAIRALI-MANAGED-UPDATE-WORKFLOW.md",
        format: "MD",
      },
    ],
  },
  {
    title: "Homework",
    description: "Daily Email and Full Drive Index are required. TEST 25 proves Drive setup only. Saturday LinkedIn is optional after both pass.",
    items: [
      {
        label: "Homework pack",
        description: "Guide, prompts, video, captions, go-live checklist and three starters: chosen-time daily email brief, resumable FULL DRIVE INDEX, plus optional Saturday LinkedIn drafts with task-scoped local control and human-only LinkedIn access and sending.",
        file: "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK.zip",
        format: "ZIP",
      },
      {
        label: "Homework guide",
        description: "The printable employee guide, including the managed update path.",
        file: "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.pdf",
        format: "PDF",
      },
      {
        label: "Editable homework guide",
        description: "The same guide in an editable document.",
        file: "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.docx",
        format: "DOCX",
      },
      {
        label: "Homework checksum",
        description: "For IT or a technical facilitator verifying the homework ZIP.",
        file: "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK.sha256",
        format: "SHA-256",
      },
    ],
  },
  {
    title: "Editable facilitator files",
    description: "Use these only when an approved amendment must be made and revalidated.",
    items: [
      {
        label: "Editable facilitator runbook",
        description: "The room sequence and recovery guide in DOCX format.",
        file: "FACILITATOR-RUNBOOK-v9-PUBLIC-KIT.docx",
        format: "DOCX",
      },
      {
        label: "Editable print checklist",
        description: "The pre-session checklist in DOCX format.",
        file: "PRINT-CHECKLIST-v9-PUBLIC-KIT.docx",
        format: "DOCX",
      },
      {
        label: "Editable role workbook",
        description: "The mission and proof workbook in DOCX format.",
        file: "ROLE-MISSION-WORKBOOK-v8-PUBLIC-KIT.docx",
        format: "DOCX",
      },
      {
        label: "Editable Setup Helper card",
        description: "The exact rescue prompt card in DOCX format.",
        file: "SETUP-HELPER-CARD-v7-PUBLIC-KIT.docx",
        format: "DOCX",
      },
    ],
  },
  {
    title: "Present and facilitate",
    description: "Use these in the room. The beginner deck stays command-free.",
    items: [
      {
        label: "Main presentation",
        description: "The 26-slide company rollout presentation.",
        file: "KAIRALI-AI-METHOD-DECK-v16-PUBLIC-KIT.pptx",
        format: "PPTX",
      },
      {
        label: "Main presentation PDF",
        description: "A read-only copy for review and printing.",
        file: "KAIRALI-AI-METHOD-DECK-v16-PUBLIC-KIT.pdf",
        format: "PDF",
      },
      {
        label: "Facilitator runbook",
        description: "Room sequence, recovery and completion checks.",
        file: "FACILITATOR-RUNBOOK-v9-PUBLIC-KIT.pdf",
        format: "PDF",
      },
      {
        label: "Print checklist",
        description: "A short pre-session and handout check.",
        file: "PRINT-CHECKLIST-v9-PUBLIC-KIT.pdf",
        format: "PDF",
      },
    ],
  },
  {
    title: "Optional technical clinic",
    description: "For technical volunteers after the beginner rollout ends.",
    items: [
      {
        label: "Advanced presentation",
        description: "Git, CLI, evidence review and governed role skills.",
        file: "KAIRALI-AI-METHOD-ADVANCED-CLI-BONUS-v8-PUBLIC-KIT.pptx",
        format: "PPTX",
      },
      {
        label: "Advanced presentation PDF",
        description: "A read-only copy of the technical clinic.",
        file: "KAIRALI-AI-METHOD-ADVANCED-CLI-BONUS-v8-PUBLIC-KIT.pdf",
        format: "PDF",
      },
      {
        label: "Capability and skills guide",
        description: "Apps, skills, MCP, CLI and the Akshar and Rahul opt-in boundary.",
        file: "ADVANCED-CAPABILITY-AND-TRAINER-SKILLS-GUIDE-v6-PUBLIC-KIT.pdf",
        format: "PDF",
      },
      {
        label: "Editable capability guide",
        description: "The same technical guide in an editable document.",
        file: "ADVANCED-CAPABILITY-AND-TRAINER-SKILLS-GUIDE-v6-PUBLIC-KIT.docx",
        format: "DOCX",
      },
    ],
  },
];
