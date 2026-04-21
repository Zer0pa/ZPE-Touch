# FAQ

## What is in scope?

Four bounded adopters:

- contact
- thermal
- vibrotactile
- proprioceptive

## What stays out of scope?

- affective touch
- full embodied touch
- ambient thermal scene modeling
- non-`RA_II` vibrotactile semantics
- full-body kinematics

## Is the repo self-contained?

Yes. The local verification and packaging surface needed by this repo lives inside this repo.

## Why are contact and the other fibers separated?

Because the repo keeps the contact base frozen and evaluates each non-contact fiber independently. Success on one branch does not change the truth of any other branch.
