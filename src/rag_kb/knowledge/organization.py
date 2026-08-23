"""Intelligent knowledge organization module for automatic classification and tagging."""

from typing import Dict, List, Optional, Any
import re
from collections import Counter
from pathlib import Path


class SmartKnowledgeOrganizer:
    """Intelligent organizer for automatic knowledge classification and tagging."""
    
    def __init__(self):
        """Initialize smart knowledge organizer."""
        self.category_keywords = {
            'technical': ['技术', '架构', '开发', '编程', 'API', '数据库', '算法', '框架', '系统', '部署'],
            'product': ['产品', '需求', '功能', '用户', '市场', '竞品', '设计', '体验', '定价', '发布'],
            'project': ['项目', '计划', '进度', '团队', '管理', '里程碑', '风险', '资源', '预算', '时间'],
            'business': ['业务', '流程', '规范', '制度', '政策', '战略', '目标', 'KPI', '绩效', '报告'],
            'legal': ['法律', '合同', '协议', '条款', '合规', '知识产权', '专利', '商标', '许可', '法规']
        }
        
        self.tech_keywords = ['Python', 'Java', 'JavaScript', 'React', 'Vue', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'SQL', 'NoSQL', 'MongoDB', 'Redis', 'PostgreSQL', 'MySQL', 'Git', 'CI/CD', 'DevOps', '微服务', 'REST', 'GraphQL', 'API', 'SDK', '框架', '库', '工具']
        
        self.business_keywords = ['市场', '销售', '营销', '客户', '用户', '增长', '收入', '利润', '成本', '预算', '投资', '融资', '估值', '战略', '竞争', '分析', '报告', '数据', '指标', 'KPI']
    
    def organize_document(self, content: str, filename: str = '') -> Dict[str, Any]:
        """Organize a document with automatic classification and tagging.
        
        Args:
            content: Document content
            filename: Optional filename for additional context
            
        Returns:
            Dictionary with classification, tags, and suggestions
        """
        # Detect category
        category = self.detect_category(content, filename)
        
        # Extract tags
        tags = self.extract_tags(content, filename)
        
        # Extract entities
        entities = self.extract_entities(content)
        
        # Suggest folder
        suggested_folder = self.suggest_folder(category)
        
        # Generate summary
        summary = self.generate_summary(content)
        
        return {
            'category': category,
            'tags': tags,
            'entities': entities,
            'suggested_folder': suggested_folder,
            'summary': summary,
            'confidence': self.calculate_confidence(content, category, tags)
        }
    
    def detect_category(self, content: str, filename: str = '') -> str:
        """Detect document category based on content and filename.
        
        Args:
            content: Document content
            filename: Optional filename
            
        Returns:
            Detected category
        """
        content_lower = content.lower()
        filename_lower = filename.lower() if filename else ''
        
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                score += content_lower.count(keyword.lower())
                score += filename_lower.count(keyword.lower())
            category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'general'
    
    def extract_tags(self, content: str, filename: str = '') -> List[str]:
        """Extract relevant tags from document content.
        
        Args:
            content: Document content
            filename: Optional filename
            
        Returns:
            List of extracted tags
        """
        tags = []
        content_lower = content.lower()
        
        # Extract technical keywords
        for keyword in self.tech_keywords:
            if keyword.lower() in content_lower:
                tags.append(keyword)
        
        # Extract business keywords
        for keyword in self.business_keywords:
            if keyword.lower() in content_lower:
                tags.append(keyword)
        
        # Extract from filename
        if filename:
            filename_tags = re.findall(r'[\w-]+', filename)
            tags.extend([tag for tag in filename_tags if len(tag) > 2])
        
        # Remove duplicates and limit to top 10
        tags = list(set(tags))
        return tags[:10]
    
    def extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract named entities from document content.
        
        Args:
            content: Document content
            
        Returns:
            Dictionary of entity types and their values
        """
        entities = {
            'organizations': [],
            'technologies': [],
            'dates': [],
            'numbers': [],
            'emails': [],
            'urls': []
        }
        
        # Extract organizations (simplified)
        org_patterns = [r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', r'([A-Z]{2,})']
        for pattern in org_patterns:
            matches = re.findall(pattern, content)
            entities['organizations'].extend(matches)
        
        # Extract technologies
        for tech in self.tech_keywords:
            if tech in content:
                entities['technologies'].append(tech)
        
        # Extract dates
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{4}年\d{1,2}月\d{1,2}日'
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            entities['dates'].extend(matches)
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = re.findall(email_pattern, content)
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        entities['urls'] = re.findall(url_pattern, content)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def suggest_folder(self, category: str) -> str:
        """Suggest folder path based on category.
        
        Args:
            category: Document category
            
        Returns:
            Suggested folder path
        """
        folder_mapping = {
            'technical': '技术文档',
            'product': '产品资料',
            'project': '项目文档',
            'business': '业务文档',
            'legal': '法律文档',
            'general': '其他文档'
        }
        return folder_mapping.get(category, '其他文档')
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a brief summary of the document.
        
        Args:
            content: Document content
            max_length: Maximum summary length
            
        Returns:
            Document summary
        """
        # Simple summary: first paragraph or first 200 characters
        paragraphs = content.split('\n\n')
        if paragraphs:
            first_paragraph = paragraphs[0].strip()
            if len(first_paragraph) > max_length:
                return first_paragraph[:max_length] + '...'
            return first_paragraph
        return content[:max_length] + '...' if len(content) > max_length else content
    
    def calculate_confidence(self, content: str, category: str, tags: List[str]) -> float:
        """Calculate confidence score for classification.
        
        Args:
            content: Document content
            category: Detected category
            tags: Extracted tags
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence if we have good category match
        if category != 'general':
            confidence += 0.2
        
        # Increase confidence if we have tags
        if len(tags) >= 3:
            confidence += 0.2
        elif len(tags) >= 1:
            confidence += 0.1
        
        # Increase confidence if content is substantial
        if len(content) > 500:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def suggest_related_docs(self, doc_id: str, all_docs: List[Dict]) -> List[Dict]:
        """Suggest related documents based on content similarity.
        
        Args:
            doc_id: Current document ID
            all_docs: List of all documents
            
        Returns:
            List of related documents with similarity scores
        """
        current_doc = next((doc for doc in all_docs if doc.get('id') == doc_id), None)
        if not current_doc:
            return []
        
        current_tags = set(current_doc.get('tags', []))
        current_category = current_doc.get('category', '')
        
        related = []
        for doc in all_docs:
            if doc.get('id') == doc_id:
                continue
            
            # Calculate similarity based on tags
            doc_tags = set(doc.get('tags', []))
            tag_similarity = len(current_tags & doc_tags) / max(len(current_tags | doc_tags), 1)
            
            # Category match bonus
            category_bonus = 0.3 if doc.get('category') == current_category else 0
            
            similarity = tag_similarity + category_bonus
            
            if similarity > 0.1:
                related.append({
                    'document': doc,
                    'similarity': similarity
                })
        
        # Sort by similarity and return top 5
        related.sort(key=lambda x: x['similarity'], reverse=True)
        return related[:5]


class KnowledgeQualityAnalyzer:
    """Analyze knowledge quality and provide improvement suggestions."""
    
    def __init__(self):
        """Initialize knowledge quality analyzer."""
        self.quality_metrics = {
            'completeness': 0.0,
            'relevance': 0.0,
            'accuracy': 0.0,
            'readability': 0.0
        }
    
    def analyze_document_quality(self, content: str, metadata: Dict) -> Dict[str, Any]:
        """Analyze the quality of a document.
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            Quality analysis results
        """
        analysis = {
            'overall_score': 0.0,
            'metrics': {},
            'issues': [],
            'suggestions': []
        }
        
        # Analyze completeness
        completeness = self.analyze_completeness(content, metadata)
        analysis['metrics']['completeness'] = completeness
        
        # Analyze readability
        readability = self.analyze_readability(content)
        analysis['metrics']['readability'] = readability
        
        # Analyze structure
        structure = self.analyze_structure(content)
        analysis['metrics']['structure'] = structure
        
        # Calculate overall score
        analysis['overall_score'] = (completeness + readability + structure) / 3
        
        # Generate suggestions
        analysis['suggestions'] = self.generate_suggestions(analysis['metrics'])
        
        return analysis
    
    def analyze_completeness(self, content: str, metadata: Dict) -> float:
        """Analyze document completeness.
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            Completeness score (0-1)
        """
        score = 0.5
        
        # Check if content is substantial
        if len(content) > 1000:
            score += 0.2
        elif len(content) > 500:
            score += 0.1
        
        # Check if metadata is complete
        required_fields = ['title', 'category', 'tags']
        missing_fields = [field for field in required_fields if not metadata.get(field)]
        if not missing_fields:
            score += 0.3
        else:
            score -= 0.1 * len(missing_fields)
        
        return min(max(score, 0), 1)
    
    def analyze_readability(self, content: str) -> float:
        """Analyze document readability.
        
        Args:
            content: Document content
            
        Returns:
            Readability score (0-1)
        """
        # Simple readability analysis
        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Ideal sentence length is 15-20 words
        if 15 <= avg_sentence_length <= 20:
            score = 1.0
        elif 10 <= avg_sentence_length <= 25:
            score = 0.8
        elif 5 <= avg_sentence_length <= 30:
            score = 0.6
        else:
            score = 0.4
        
        return score
    
    def analyze_structure(self, content: str) -> float:
        """Analyze document structure.
        
        Args:
            content: Document content
            
        Returns:
            Structure score (0-1)
        """
        score = 0.5
        
        # Check for headings
        if re.search(r'^#+\s', content, re.MULTILINE):
            score += 0.2
        
        # Check for lists
        if re.search(r'^\s*[-*+]\s', content, re.MULTILINE):
            score += 0.1
        
        # Check for paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def generate_suggestions(self, metrics: Dict) -> List[str]:
        """Generate improvement suggestions based on metrics.
        
        Args:
            metrics: Quality metrics
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        if metrics.get('completeness', 0) < 0.7:
            suggestions.append('建议补充文档元数据（标题、分类、标签）')
            suggestions.append('建议增加文档内容长度')
        
        if metrics.get('readability', 0) < 0.7:
            suggestions.append('建议优化句子长度，提高可读性')
            suggestions.append('建议使用更简洁的表达方式')
        
        if metrics.get('structure', 0) < 0.7:
            suggestions.append('建议添加标题和子标题')
            suggestions.append('建议使用列表来组织内容')
        
        return suggestions