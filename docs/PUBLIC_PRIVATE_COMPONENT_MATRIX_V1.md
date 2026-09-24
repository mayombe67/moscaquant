# Public / Private Component Matrix v1

| Component | Public `moscaquant` | Private stack | Rule |
| --- | --- | --- | --- |
| Scientific protocols | Yes | Optional mirrors | Required for reproducible claims |
| Published configs | Yes | Deployment overrides | Secrets/host details stay private |
| Authoritative scientific execution contract | Yes | Provider-specific implementation | Runtime acceptance and scientific invariants are public |
| Execution provenance / immutable digests | Yes | Raw operational extras may also exist | Published execution claims remain auditable |
| RASPUTIN provider IaC / operator internals | No | Yes | Operations private; scientific contract public |
| Result summaries | Yes | Raw/private extras optional | Published claims need evidence |
| Provenance / RECEIPTS | Yes | Private raw receipts may also exist | Public claims remain auditable |
| OVERWATCH schemas | Yes | Production transport | Contract public, operations private |
| Motor/physics contracts | Yes | Production solver adapters may be private | Publish enough for claims |
| Public projection rules | Yes | Sanitizer deployment | Public boundary itself is auditable |
| Minimal replay format | Yes | Production replay UX | Evidence open, experience protected |
| Debug/reference renderer | Yes | High-fidelity Panopticon | Public proves contract |
| CELL-67 schema | Yes | Production scene/assets | Environment identity public |
| 3D MORTY production rig | No | Yes | Product/art IP |
| Classified modifier catalog | No | Yes | Public sees only disclosed/unlocked items |
| Sponsor system | Thin public events/contracts | Yes | Commercial internals private |
| Referendum voting backend | Thin public result/receipt contract | Yes | Anti-abuse/identity private |
| Meme deck | No | Yes | Presentation only |
| Achievements content library | Optional thin IDs | Yes | Presentation/content IP |
| Broadcast/social bots | No | Yes | Product/ops |
| Broker/execution adapters | No | Yes | Operationally sensitive |
| Warden public interface | Yes where needed | Enforcement wiring private | Authority semantics remain auditable |
| Credentials/secrets | Never | Yes | Private only |
| Restricted/licensed datasets | No | Secure data storage | Publish hashes/metadata where lawful |
| Public experiment datasets | Yes when licensed/appropriate | Optional | Prefer reproducibility |
| Commercial analytics | No | Yes | Product layer |

## Decision rule

When uncertain:

> If researchers need it to evaluate the claim, open it.

> If users need it to enjoy the product, it may remain private.

> If attackers need it to weaken containment or operations, keep it private.
