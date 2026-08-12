# Business Requirements Document

**BRD ID:** BRD-2026-014
**Title:** Global Greeting Service
**Sponsor:** Digital Experience, Business Technology
**Author:** Business Analyst (persona: Priya)
**Status:** Approved by business — handed off to engineering
**Date:** 2026-07-28

---

## 1. Business Context

As part of the global customer-experience initiative, customer-facing
applications must greet users in their preferred language. Today each
application implements its own greeting text, leading to inconsistent
tone and duplicated translation costs.

## 2. Business Requirements

> Written in typical BRD prose — deliberately underspecified, as real
> BRDs are. The gaps are surfaced in the spec's Ambiguity Log.

- **BR-1.** The system shall provide a greeting to the calling
  application appropriate to the user's language preference.
- **BR-2.** The greeting must be available to all regional applications.
- **BR-3.** The system should handle situations where a language is not
  supported.
- **BR-4.** The system must be monitorable by operations.

## 3. Out of Scope

- Personalization (user names, time-of-day variants)
- Translation workflow / content management

## 4. Success Criteria

- Regional apps can retrieve greetings via a standard interface.
- Operations can verify service health.
