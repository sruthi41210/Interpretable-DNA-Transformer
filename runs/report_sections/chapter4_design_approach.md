# **CHAPTER 4: DESIGN APPROACH AND DETAILS**

## 4.1 SYSTEM ARCHITECTURE

The DNA-SLM system follows a modular pipeline architecture, consisting of the following major subsystems:

1.  **Data Ingestion:** Reads raw DNA sequences from CSV/FASTA files and performs preprocessing.
2.  **Tokenization:** Converts nucleotide sequences (A, C, G, T) into integer tokens using a character-level tokenizer.
3.  **Model Training:** Trains the TinyDNAEncoder (Baseline or ALiBi) using Automatic Mixed Precision and early stopping.
4.  **Evaluation:** Computes performance metrics (AUROC, PR-AUC, ECE) on the held-out test set.
5.  **Interpretability:** Runs K-mer enrichment and In-Silico Mutagenesis to discover high-importance sequence windows.
6.  **Validation:** Matches extracted PWMs against the JASPAR database and performs statistical enrichment tests.

> **[IMAGE PLACEMENT: `runs/diagrams/system_architecture.png` - High-level pipeline diagram]**

---

## 4.2 DESIGN

### 4.2.1 Data Flow Diagram (DFD)

The Data Flow Diagram illustrates how information moves through the system from input (raw sequences) to output (validated motifs and predictions).

**Level 0 DFD (Context Diagram):**

```plantuml
@startuml
!theme plain
skinparam roundcorner 10

actor "Researcher" as user
rectangle "DNA-SLM System" as system
database "JASPAR\nDatabase" as jaspar
database "Sequence\nDataset" as data

user --> system : Provides Sequences
data --> system : Raw DNA Sequences
system --> user : Classification Results\n+ Validated Motifs
system --> jaspar : Query for\nTF Match
jaspar --> system : TF Binding Profile
@enduml
```

**Level 1 DFD:**

```plantuml
@startuml
!theme plain
skinparam roundcorner 10

database "Sequence CSV" as input
rectangle "1.0 Tokenization" as tok
rectangle "2.0 Model Training" as train
rectangle "3.0 Prediction" as pred
rectangle "4.0 ISM Analysis" as ism
rectangle "5.0 JASPAR Match" as jaspar
database "Checkpoint.pt" as ckpt
database "ISM_Windows.csv" as ismout
actor "Researcher" as user

input --> tok : Raw Sequences
tok --> train : Token Tensors
train --> ckpt : Save Model Weights
ckpt --> pred : Load Model
input --> pred : Test Sequences
pred --> ism : High-Confidence Predictions
ism --> ismout : High-Importance Windows
ismout --> jaspar : PWMs
jaspar --> user : Validated Motifs (TFAP2A)
@enduml
```

> **[IMAGE PLACEMENT: Generate `runs/diagrams/dfd_level0.png` and `runs/diagrams/dfd_level1.png` from PlantUML above]**

---

### 4.2.2 Class Diagram

The Class Diagram shows the object-oriented structure of key components.

```plantuml
@startuml
!theme plain
skinparam classAttributeIconSize 0

class CharTokenizer {
  +vocab: dict
  +pad_token: int
  +encode(seq: str): list
  +decode(tokens: list): str
}

class TinyDNAEncoder {
  +tok_emb: nn.Embedding
  +pos_emb: nn.Embedding
  +layers: nn.ModuleList
  +cls_head: nn.Linear
  +forward(x): Tensor
}

class TinyDNAEncoderALiBi {
  +alibi_bias: Tensor
  +forward(x): Tensor
}

class DNADataset {
  +data: DataFrame
  +tokenizer: CharTokenizer
  +max_len: int
  +__getitem__(idx): tuple
  +__len__(): int
}

class Trainer {
  +model: TinyDNAEncoder
  +optimizer: AdamW
  +scaler: GradScaler
  +train_epoch(loader): float
  +validate(loader): float
}

class ISMAnalyzer {
  +model: TinyDNAEncoder
  +mutate_and_score(seq, window): float
  +get_importance_curve(seq): np.array
}

class JASPARMatcher {
  +jaspar_db: list
  +compare_pwm(pwm): tuple
}

TinyDNAEncoderALiBi --|> TinyDNAEncoder : extends
Trainer --> TinyDNAEncoder : uses
DNADataset --> CharTokenizer : uses
ISMAnalyzer --> TinyDNAEncoder : uses
JASPARMatcher --> ISMAnalyzer : receives PWMs from
@enduml
```

> **[IMAGE PLACEMENT: Generate `runs/diagrams/class_diagram.png` from PlantUML above]**

---

## 4.3 MODULE INTERACTION

The following diagram illustrates how software modules interact during a typical execution run.

> **[IMAGE PLACEMENT: `runs/diagrams/module_interaction.png` - Already generated]**
