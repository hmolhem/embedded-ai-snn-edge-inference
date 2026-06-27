# Minimal Course Project Proposal Draft

## Proposed Title

**Lightweight Spike-Based Edge Inference for Embedded Sensing**

## Problem Statement

Edge-AI systems often operate under strict power, memory, and latency constraints. Conventional dense neural-network inference may be inefficient for always-on sensing tasks, especially when the useful information is sparse or event-like. This project investigates a small spike-based inference workflow for simulated embedded sensing data.

## Objective

The objective is to build a minimal Python prototype that converts normalized sensing features into spike-like representations and evaluates a lightweight LIF-inspired classifier.

## Scope

The project is intentionally modest. It does not claim to build a full neuromorphic chip, a complete robotic autonomy stack, or a hardware accelerator. The focus is on understanding spike encoding, sparse temporal activity, and edge-oriented metrics.

## Method

1. Generate or simulate a small sensing dataset.
2. Normalize the feature vectors.
3. Convert features into spike-like representations using rate coding or a simple temporal encoding.
4. Apply a lightweight LIF-inspired classifier.
5. Evaluate classification accuracy, confusion matrix, average spike count, and latency in time steps.

## Expected Deliverables

- Python implementation
- result figures
- metrics table
- short report
- discussion of future embedded/PYNQ/FPGA extension
